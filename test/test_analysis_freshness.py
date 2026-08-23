from datetime import (
    datetime,
    timedelta,
    timezone,
)
from types import SimpleNamespace

from cache.option_chain_cache import CACHE_TTL_SECONDS
from graph.nodes import OptionGraphNodes
from schemas.analysis_request import AnalysisRequest


class FakeMarketTimeTool:

    def get_market_context(self):
        return SimpleNamespace(
            current_time=datetime(
                2026,
                8,
                17,
                10,
                0,
                tzinfo=timezone.utc,
            )
        )


class FakeNaturalDateResolver:

    def resolve(
        self,
        user_input: str,
        market_date,
    ):
        return None


class FakeDecisionAgent:

    def __init__(self):
        self.last_kwargs = None

    def decide_next_action(self, **kwargs):
        self.last_kwargs = kwargs

        return {
            "decision_type": "final_answer",
            "content": "fake direct answer",
        }


class FakeExecutionAgent:

    def execute_tool_call(
        self,
        tool_name: str,
        arguments_json: str,
    ):
        return {
            "request": AnalysisRequest(
                ticker="TSLA",
                expiration="2026-08-21",
                analysis_types=["gex"],
            ),
            "analysis_result": object(),
            "analysis_context": "fake analysis context",
        }


def build_nodes(agent):

    nodes = OptionGraphNodes(agent)

    nodes.market_time_tool = FakeMarketTimeTool()
    nodes.natural_date_resolver = (
        FakeNaturalDateResolver()
    )

    return nodes


def test_execute_tool_call_writes_timestamp():

    nodes = build_nodes(
        FakeExecutionAgent()
    )

    result = nodes.execute_tool_call_node(
        {
            "agent_decision": {
                "decision_type": "tool_call",
                "tool_name": "run_option_analysis",
                "arguments_json": (
                    '{"ticker":"TSLA"}'
                ),
            }
        }
    )

    assert result["last_successful_at"]

    completed_at = datetime.fromisoformat(
        result["last_successful_at"]
    )

    assert completed_at.tzinfo is not None

    print(
        "Tool execution timestamp test passed."
    )


def test_freshness_check():

    nodes = build_nodes(
        FakeDecisionAgent()
    )

    fresh_state = {
        "analysis_context": "fresh data",
        "last_successful_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    assert nodes._has_fresh_analysis_context(
        fresh_state
    ) is True

    stale_state = {
        "analysis_context": "old data",
        "last_successful_at": (
            datetime.now(timezone.utc)
            - timedelta(
                seconds=CACHE_TTL_SECONDS + 1
            )
        ).isoformat(),
    }

    assert nodes._has_fresh_analysis_context(
        stale_state
    ) is False

    no_timestamp_state = {
        "analysis_context": "legacy data",
    }

    assert nodes._has_fresh_analysis_context(
        no_timestamp_state
    ) is False

    print("Freshness check test passed.")


def test_stale_context_is_not_sent_to_llm():

    agent = FakeDecisionAgent()
    nodes = build_nodes(agent)

    stale_state = {
        "user_input": "分析 TSLA 的 GEX",
        "conversation_history": [
            {
                "role": "assistant",
                "content": "old market analysis",
            }
        ],
        "running_summary": "old summary",
        "analysis_context": "old analysis context",
        "last_successful_request": {
            "ticker": "TSLA",
            "expiration": "2026-08-21",
            "analysis_types": ["gex"],
        },
        "last_successful_at": (
            datetime.now(timezone.utc)
            - timedelta(
                seconds=CACHE_TTL_SECONDS + 1
            )
        ).isoformat(),
    }

    nodes.agent_decide_node(stale_state)

    assert agent.last_kwargs[
        "conversation_history"
    ] == []

    assert agent.last_kwargs[
        "running_summary"
    ] is None

    assert agent.last_kwargs[
        "analysis_context"
    ] is None

    assert agent.last_kwargs[
        "has_fresh_analysis"
    ] is False

    assert agent.last_kwargs[
        "last_successful_request"
    ]["ticker"] == "TSLA"

    print(
        "Stale context isolation test passed."
    )


def test_fresh_context_is_sent_to_llm():

    agent = FakeDecisionAgent()
    nodes = build_nodes(agent)

    fresh_state = {
        "user_input": "再详细解释一下",
        "conversation_history": [
            {
                "role": "assistant",
                "content": "fresh market analysis",
            }
        ],
        "running_summary": "fresh summary",
        "analysis_context": "fresh analysis context",
        "last_successful_request": {
            "ticker": "TSLA",
            "expiration": "2026-08-21",
            "analysis_types": ["gex"],
        },
        "last_successful_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    nodes.agent_decide_node(fresh_state)

    assert agent.last_kwargs[
        "conversation_history"
    ] == fresh_state["conversation_history"]

    assert agent.last_kwargs[
        "running_summary"
    ] == "fresh summary"

    assert agent.last_kwargs[
        "analysis_context"
    ] == "fresh analysis context"

    assert agent.last_kwargs[
        "has_fresh_analysis"
    ] is True

    print(
        "Fresh context forwarding test passed."
    )


if __name__ == "__main__":
    test_execute_tool_call_writes_timestamp()
    test_freshness_check()
    test_stale_context_is_not_sent_to_llm()
    test_fresh_context_is_sent_to_llm()

    print(
        "All analysis freshness tests passed."
    )