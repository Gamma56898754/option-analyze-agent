from graph.state import OptionAgentState



def route_after_validation(
    state: OptionAgentState,
) -> str:

    if state.get("validation_error"):
        return "invalid"

    request = state["request"]

    if (
        request.execution_mode
        == "explain_existing"
        and state.get("analysis_context")
    ):
        print(
            "Route: explain existing analysis"
        )

        return "explain_existing"

    print(
        "Route: run analysis"
    )

    return "run_analysis"


SUMMARY_TRIGGER_MESSAGES = 12


def route_after_short_term_memory(
    state: OptionAgentState,
) -> str:

    history = state.get(
        "conversation_history",
        []
    )

    if len(history) >= SUMMARY_TRIGGER_MESSAGES:
        return "summarize"

    return "end"

def route_after_analysis(
    state: OptionAgentState,
) -> str:

    if state.get("analysis_error"):
        return "failed"

    return "success"

def route_after_agent_decision(
    state: OptionAgentState,
) -> str:

    decision = state.get(
        "agent_decision"
    )

    if decision is None:

        raise ValueError(
            "Missing agent decision"
        )

    decision_type = decision.get(
        "decision_type"
    )

    if decision_type == "tool_call":

        print(
            "Route: execute tool call"
        )

        return "tool_call"

    if decision_type == "final_answer":

        print(
            "Route: direct answer"
        )

        return "final_answer"

    raise ValueError(
        "Unsupported agent decision type: "
        f"{decision_type}"
    )


def route_after_tool_execution(
    state: OptionAgentState,
) -> str:

    if state.get("loop_termination_reason"):

        return "loop_terminated"

    if state.get("validation_error"):

        return "invalid"

    if state.get("analysis_error"):

        return "failed"

    return "continue"
