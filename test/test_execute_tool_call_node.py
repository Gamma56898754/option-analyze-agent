from core.exceptions import (
    ExpirationNotFoundError,
)

from graph.nodes import OptionGraphNodes
from schemas.analysis_request import AnalysisRequest


class FakeSuccessAgent:

    def __init__(self):

        self.tool_name = None

        self.arguments_json = None

    def execute_tool_call(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):

        self.tool_name = tool_name

        self.arguments_json = arguments_json

        request = AnalysisRequest(
            ticker="TSLA",
            expiration="2026-08-21",
            analysis_types=["gex"],
        )

        return {
            "request": request,
            "analysis_result": (
                "fake-analysis-result"
            ),
            "analysis_context": (
                "fake-analysis-context"
            ),
        }


class FakeExpirationErrorAgent:

    def execute_tool_call(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):

        raise ExpirationNotFoundError(
            ticker="TSLA",
            requested_expiration=(
                "2026-08-20"
            ),
            available_expirations=[
                "2026-08-21",
                "2026-08-24",
            ],
        )


def test_execute_tool_call_node_success():

    node = OptionGraphNodes.__new__(
        OptionGraphNodes
    )

    node.agent = FakeSuccessAgent()

    result = node.execute_tool_call_node(
        {
            "agent_decision": {
                "decision_type": "tool_call",
                "tool_name": (
                    "run_option_analysis"
                ),
                "arguments_json": (
                    '{"ticker":"TSLA"}'
                ),
            }
        }
    )

    assert node.agent.tool_name == (
        "run_option_analysis"
    )

    assert node.agent.arguments_json == (
        '{"ticker":"TSLA"}'
    )

    assert result["request"].ticker == "TSLA"

    assert result["analysis_context"] == (
        "fake-analysis-context"
    )

    assert result["analysis_error"] is None


def test_execute_tool_call_node_expiration_error():

    node = OptionGraphNodes.__new__(
        OptionGraphNodes
    )

    node.agent = FakeExpirationErrorAgent()

    result = node.execute_tool_call_node(
        {
            "agent_decision": {
                "decision_type": "tool_call",
                "tool_name": (
                    "run_option_analysis"
                ),
                "arguments_json": (
                    '{"ticker":"TSLA"}'
                ),
            }
        }
    )

    assert result["analysis_error"] == (
        "expiration_not_found"
    )

    assert result["request"].ticker == "TSLA"

    assert result["request"].expiration == (
        "2026-08-20"
    )

    assert result["available_expirations"] == [
        "2026-08-21",
        "2026-08-24",
    ]


if __name__ == "__main__":

    test_execute_tool_call_node_success()

    test_execute_tool_call_node_expiration_error()

    print(
        "Execute tool call node test passed."
    )
