"""Local stdio MCP server for the existing option-analysis tool."""

from functools import lru_cache

from mcp.server.mcpserver import MCPServer

from agent.result_formatter import ResultFormatter
from agent.tool_calling.tool_executor import OptionToolExecutor
from core.analysis_runner import AnalysisRunner
from core.request_validator import RequestValidator
from core.runtime import Runtime
from mcp_server.option_service import run_option_analysis_tool


@lru_cache(maxsize=1)
def get_option_tool_executor() -> OptionToolExecutor:
    """Create long-lived runtime dependencies only when a tool is called."""

    runtime = Runtime()

    return OptionToolExecutor(
        runner=AnalysisRunner(runtime),
        validator=RequestValidator(),
        formatter=ResultFormatter(),
    )


def create_option_mcp_server(
    executor_factory=get_option_tool_executor,
) -> MCPServer:
    """Build a testable MCP server around the stable existing executor."""

    server = MCPServer(
        name="Option Analysis MCP Server",
    )

    @server.tool()
    def run_option_analysis(
        ticker: str,
        expiration: str,
        analysis_types: list[str],
        force_refresh: bool = False,
    ) -> dict[str, object]:
        """Retrieve a US option chain and calculate GEX, DEX, OI, or max pain."""

        return run_option_analysis_tool(
            executor=executor_factory(),
            ticker=ticker,
            expiration=expiration,
            analysis_types=analysis_types,
            force_refresh=force_refresh,
        )

    return server


mcp = create_option_mcp_server()


def main() -> None:
    """Run the server over stdio for a local MCP host."""

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
