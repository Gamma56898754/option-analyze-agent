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