"""MCP-independent adapter for the existing option tool executor."""

import json
from datetime import datetime
from uuid import uuid4

from agent.tool_calling.tool_executor import OptionToolExecutor
from core.exceptions import (
    ExpirationNotFoundError,
    MarketDataUnavailableError,
)


def serialize_data_quality_report(
    report,
) -> dict[str, object] | None:
    """Convert the internal report into a stable JSON-ready MCP value."""

    if report is None:
        return None

    fetched_at = report.fetched_at

    if isinstance(fetched_at, datetime):
        fetched_at_value = fetched_at.isoformat()
    else:
        fetched_at_value = str(fetched_at)

    return {
        "source": report.source,
        "fetched_at": fetched_at_value,
        "cache_state": report.cache_state,
        "contract_count": report.contract_count,
        "warnings": report.warnings,
    }


def run_option_analysis_tool(
    executor: OptionToolExecutor,
    ticker: str,
    expiration: str,
    analysis_types: list[str],
    force_refresh: bool = False,
) -> dict[str, object]:
    """Execute the existing option tool and return an MCP-safe response."""

    trace_id = uuid4().hex
    arguments = {
        "ticker": ticker,
        "expiration": expiration,
        "analysis_types": analysis_types,
        "force_refresh": force_refresh,
    }

    try:
        execution_result = executor.execute(
            tool_name=OptionToolExecutor.TOOL_NAME,
            arguments_json=json.dumps(arguments),
            trace_id=trace_id,
        )

    except ExpirationNotFoundError as exc:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": "expiration_not_found",
                "message": (
                    f"No option chain is available for {exc.ticker} "
                    f"on {exc.requested_expiration}."
                ),
                "available_expirations": exc.available_expirations,
            },
        }

    except MarketDataUnavailableError as exc:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": "market_data_unavailable",
                "message": "The option market data source is unavailable.",
                "source": exc.source,
                "operation": exc.operation,
                "status_code": exc.status_code,
            },
        }

    except ValueError as exc:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": "invalid_request",
                "message": str(exc),
            },
        }

    except Exception:
        return {
            "ok": False,
            "trace_id": trace_id,
            "error": {
                "code": "internal_error",
                "message": "The option analysis could not be completed.",
            },
        }

    request = execution_result["request"]
    analysis_result = execution_result["analysis_result"]

    return {
        "ok": True,
        "trace_id": trace_id,
        "request": {
            "ticker": request.ticker,
            "expiration": request.expiration,
            "analysis_types": request.analysis_types,
            "force_refresh": request.force_refresh,
        },
        "analysis_context": execution_result["analysis_context"],
        "data_quality": serialize_data_quality_report(
            analysis_result.data_quality_report
        ),
    }
