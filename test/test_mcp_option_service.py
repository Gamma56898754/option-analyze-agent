from datetime import datetime, timezone

from core.exceptions import ExpirationNotFoundError
from mcp_server.option_service import run_option_analysis_tool
from schemas.analysis_request import AnalysisRequest
from schemas.analysis_result import AnalysisResult
from schemas.data_quality_report import DataQualityReport


class FakeExecutor:

    def execute(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):
        return {
            "request": AnalysisRequest(
                ticker="TSLA",
                expiration="2026-08-28",
                analysis_types=["gex"],
            ),
            "analysis_result": AnalysisResult(
                ticker="TSLA",
                expiration="2026-08-28",
                data_quality_report=DataQualityReport(
                    source="OptionCharts",
                    fetched_at=datetime(
                        2026,
                        8,
                        24,
                        tzinfo=timezone.utc,
                    ),
                    cache_state="miss",
                    contract_count=100,
                ),
            ),
            "analysis_context": "Ticker: TSLA",
        }


class ExpirationFailingExecutor:

    def execute(self, *args, **kwargs):
        raise ExpirationNotFoundError(
            ticker="TSLA",
            requested_expiration="2035-01-01",
            available_expirations=["2026-08-28"],
        )


def test_mcp_service_returns_json_safe_success_response():

    response = run_option_analysis_tool(
        executor=FakeExecutor(),
        ticker="tsla",
        expiration="2026-08-28",
        analysis_types=["gex"],
    )

    assert response["ok"] is True
    assert response["request"]["ticker"] == "TSLA"
    assert response["data_quality"]["cache_state"] == "miss"
    assert response["data_quality"]["fetched_at"].endswith("+00:00")


def test_mcp_service_maps_expiration_error():

    response = run_option_analysis_tool(
        executor=ExpirationFailingExecutor(),
        ticker="TSLA",
        expiration="2035-01-01",
        analysis_types=["gex"],
    )

    assert response["ok"] is False
    assert response["error"]["code"] == "expiration_not_found"
    assert response["error"]["available_expirations"] == ["2026-08-28"]


if __name__ == "__main__":

    test_mcp_service_returns_json_safe_success_response()
    test_mcp_service_maps_expiration_error()

    print("MCP option service test passed.")
