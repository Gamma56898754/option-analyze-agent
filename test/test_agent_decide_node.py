from datetime import datetime
from types import SimpleNamespace

from graph.nodes import OptionGraphNodes


class FakeMarketTimeTool:

    def get_market_context(self):

        return SimpleNamespace(
            current_time=datetime(
                2026,
                8,
                17,
                10,
                0,
            )
        )


class FakeNaturalDateResolver:

    def resolve(
        self,
        user_input,
        market_date,
    ):

        return "2026-08-21"


class FakeAgent:

    def __init__(self):

        self.kwargs = None

    def decide_next_action(self, **kwargs):

        self.kwargs = kwargs

        return {
            "decision_type": "tool_call",
            "tool_call_id": "call_test_001",
            "tool_name": "run_option_analysis",
            "arguments_json": (
                '{"ticker":"TSLA",'
                '"expiration":"2026-08-20",'
                '"analysis_types":["gex"]}'
            ),
        }


def test_agent_decide_node():

    node = OptionGraphNodes.__new__(
        OptionGraphNodes
    )

    node.agent = FakeAgent()

    node.market_time_tool = FakeMarketTimeTool()

    node.natural_date_resolver = (
        FakeNaturalDateResolver()
    )

    result = node.agent_decide_node(
        {
            "user_input": (
                "Analyze TSLA next Friday GEX"
            ),
            "conversation_history": [],
            "analysis_context": None,
        }
    )

    decision = result["agent_decision"]

    assert decision["decision_type"] == (
        "tool_call"
    )

    assert decision["tool_name"] == (
        "run_option_analysis"
    )

    assert '"expiration": "2026-08-21"' in (
        decision["arguments_json"]
    )

    assert node.agent.kwargs[
        "resolved_expiration"
    ] == "2026-08-21"


if __name__ == "__main__":

    test_agent_decide_node()

    print("Agent decide node test passed.")