from datetime import datetime, timezone

import pytest
from mcp import Client

from mcp_server.option_server import create_option_mcp_server
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
                    cache_state="hit",
                    contract_count=100,
                ),
            ),
            "analysis_context": "Ticker: TSLA",
        }


@pytest.mark.anyio
async def test_mcp_server_registers_and_executes_option_tool():

    server = create_option_mcp_server(
        executor_factory=lambda: FakeExecutor(),
    )

    async with Client(server) as client:
        tools = await client.list_tools()

        assert [tool.name for tool in tools.tools] == [
            "run_option_analysis"
        ]

        result = await client.call_tool(
            "run_option_analysis",
            {
                "ticker": "TSLA",
                "expiration": "2026-08-28",
                "analysis_types": ["gex"],
            },
        )

    assert result.structured_content["ok"] is True
    assert result.structured_content["data_quality"][
        "cache_state"
    ] == "hit"
