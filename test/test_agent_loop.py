from graph.nodes import OptionGraphNodes
from core.exceptions import MarketDataUnavailableError


class FakeAgent:

    def __init__(self):
        self.execution_count = 0

    def execute_tool_call(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):
        self.execution_count += 1

        return {
            "request": None,
            "analysis_context": "tool result",
        }


class FakeUnavailableMarketAgent:

    def execute_tool_call(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):
        raise MarketDataUnavailableError(
            source="OptionCharts",
            operation="option_chain",
        )


def test_duplicate_tool_call_is_not_executed_twice():

    node = OptionGraphNodes.__new__(OptionGraphNodes)
    node.agent = FakeAgent()

    decision = {
        "decision_type": "tool_call",
        "tool_call_id": "call_2",
        "tool_name": "run_option_analysis",
        "arguments_json": (
            '{"ticker":"TSLA","expiration":"2026-08-21",'
            '"analysis_types":["gex"]}'
        ),
    }

    signature = node._tool_call_signature(decision)

    result = node.execute_tool_call_node(
        {
            "agent_decision": decision,
            "tool_call_signatures": [signature],
            "tool_step_count": 1,
            "max_tool_steps": 3,
        }
    )

    assert node.agent.execution_count == 0
    assert result["tool_step_count"] == 2
    assert result["tool_observations"][0]["status"] == "duplicate"


def test_loop_stops_before_exceeding_max_steps():

    node = OptionGraphNodes.__new__(OptionGraphNodes)
    node.agent = FakeAgent()

    result = node.execute_tool_call_node(
        {
            "agent_decision": {
                "decision_type": "tool_call",
                "tool_name": "run_option_analysis",
                "arguments_json": "{}",
            },
            "tool_step_count": 3,
            "max_tool_steps": 3,
        }
    )

    assert node.agent.execution_count == 0
    assert result["loop_termination_reason"] == "max_tool_steps"


def test_market_data_failure_has_a_bounded_retry_budget():

    node = OptionGraphNodes.__new__(OptionGraphNodes)
    node.agent = FakeUnavailableMarketAgent()

    decision = {
        "decision_type": "tool_call",
        "tool_call_id": "call_1",
        "tool_name": "run_option_analysis",
        "arguments_json": "{}",
    }

    first_result = node.execute_tool_call_node(
        {
            "agent_decision": decision,
            "tool_step_count": 0,
            "max_tool_steps": 3,
            "max_consecutive_tool_failures": 2,
        }
    )

    assert first_result["consecutive_tool_failure_count"] == 1
    assert first_result["tool_observations"][0]["status"] == "error"
    assert "loop_termination_reason" not in first_result

    second_result = node.execute_tool_call_node(
        {
            "agent_decision": decision,
            "tool_step_count": first_result["tool_step_count"],
            "consecutive_tool_failure_count": first_result[
                "consecutive_tool_failure_count"
            ],
            "last_failed_tool_name": "run_option_analysis",
            "max_tool_steps": 3,
            "max_consecutive_tool_failures": 2,
        }
    )

    assert second_result["consecutive_tool_failure_count"] == 2
    assert second_result["loop_termination_reason"] == (
        "max_consecutive_tool_failures"
    )


if __name__ == "__main__":

    test_duplicate_tool_call_is_not_executed_twice()
    test_loop_stops_before_exceeding_max_steps()
    test_market_data_failure_has_a_bounded_retry_budget()

    print("Agent loop tests passed.")
