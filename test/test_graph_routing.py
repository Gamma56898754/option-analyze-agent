from schemas.analysis_request import AnalysisRequest
from graph.routing import (
    route_after_analysis,
    route_after_validation,
)


def build_request(
    execution_mode: str,
) -> AnalysisRequest:

    return AnalysisRequest(
        ticker="TSLA",
        expiration="2026-08-17",
        analysis_types=["oi"],
        execution_mode=execution_mode,
    )


def main():

    invalid_state = {
        "validation_error": "Invalid ticker",
    }

    assert (
        route_after_validation(
            invalid_state
        )
        == "invalid"
    )

    analysis_state = {
        "request": build_request(
            "run_analysis"
        ),
        "analysis_context": "Previous OI context",
    }

    assert (
        route_after_validation(
            analysis_state
        )
        == "run_analysis"
    )

    explain_state = {
        "request": build_request(
            "explain_existing"
        ),
        "analysis_context": "Previous OI context",
    }

    assert (
        route_after_validation(
            explain_state
        )
        == "explain_existing"
    )

    explain_without_context_state = {
        "request": build_request(
            "explain_existing"
        ),
    }

    assert (
        route_after_validation(
            explain_without_context_state
        )
        == "run_analysis"
    )

    assert (
        route_after_analysis(
            {
                "analysis_error": None,
            }
        )
        == "success"
    )

    assert (
        route_after_analysis(
            {
                "analysis_error": (
                    "expiration_not_found"
                ),
            }
        )
        == "failed"
    )

    print("Graph routing test passed.")


if __name__ == "__main__":
    main()