from datetime import datetime, timezone

from agent.result_formatter import ResultFormatter
from schemas.analysis_result import AnalysisResult
from schemas.data_quality_report import DataQualityReport


def test_formatter_includes_quality_provenance_and_warning():

    report = DataQualityReport(
        source="OptionCharts",
        fetched_at=datetime(
            2026,
            8,
            24,
            4,
            0,
            tzinfo=timezone.utc,
        ),
        cache_state="hit",
        contract_count=0,
        warnings=[
            "The retrieved option chain contains no contracts.",
        ],
    )

    result = AnalysisResult(
        ticker="TSLA",
        expiration="2026-08-28",
        data_quality_report=report,
    )

    context = ResultFormatter().format(result)

    assert "=== DATA QUALITY ===" in context
    assert "Source: OptionCharts" in context
    assert "Cache State: hit" in context
    assert "Contract Count: 0" in context
    assert "DATA QUALITY WARNING:" in context


if __name__ == "__main__":

    test_formatter_includes_quality_provenance_and_warning()

    print("Data quality report test passed.")
