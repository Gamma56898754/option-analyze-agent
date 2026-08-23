from graph.nodes import OptionGraphNodes
from graph.routing import (
    route_after_agent_decision,
    route_after_tool_execution,
)


def test_route_after_agent_decision():

    tool_call_route = (
        route_after_agent_decision(
            {
                "agent_decision": {
                    "decision_type": "tool_call",
                }
            }
        )
    )

    assert tool_call_route == "tool_call"

    final_answer_route = (
        route_after_agent_decision(
            {
                "agent_decision": {
                    "decision_type": "final_answer",
                }
            }
        )
    )

    assert final_answer_route == (
        "final_answer"
    )


def test_route_after_tool_execution():

    success_route = (
        route_after_tool_execution(
            {
                "validation_error": None,
                "analysis_error": None,
            }
        )
    )

    assert success_route == "success"

    invalid_route = (
        route_after_tool_execution(
            {
                "validation_error": (
                    "Invalid ticker"
                ),
            }
        )
    )

    assert invalid_route == "invalid"

    failed_route = (
        route_after_tool_execution(
            {
                "analysis_error": (
                    "expiration_not_found"
                ),
            }
        )
    )

    assert failed_route == "failed"


def test_direct_answer_node():

    node = OptionGraphNodes.__new__(
        OptionGraphNodes
    )

    result = node.direct_answer_node(
        {
            "agent_decision": {
                "decision_type": "final_answer",
                "content": (
                    "Here is an explanation "
                    "of the existing analysis."
                ),
            }
        }
    )

    assert result["final_answer"] == (
        "Here is an explanation "
        "of the existing analysis."
    )


if __name__ == "__main__":

    test_route_after_agent_decision()

    test_route_after_tool_execution()

    test_direct_answer_node()

    print(
        "Tool calling routing test passed."
    )