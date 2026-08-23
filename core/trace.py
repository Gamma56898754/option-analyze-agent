import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_DIRECTORY = PROJECT_ROOT / "logs"

TRACE_LOG_PATH = (
    LOG_DIRECTORY
    / "option_agent.jsonl"
)

TRACE_LOG_LOCK = Lock()




def log_trace_event(
    trace_id: str,
    event: str,
    **fields: Any,
) -> None:
    """
    Append one structured trace event to a local JSONL file.

    Trace logging must never interrupt normal Agent execution.
    """

    payload = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "trace_id": trace_id,
        "event": event,
        **fields,
    }

    try:

        LOG_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        serialized_payload = json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

        with TRACE_LOG_LOCK:

            with TRACE_LOG_PATH.open(
                "a",
                encoding="utf-8",
            ) as log_file:

                log_file.write(
                    serialized_payload + "\n"
                )

    except OSError:
        # Observability must not make
        # the product unavailable.
        pass