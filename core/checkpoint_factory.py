import sqlite3
from pathlib import Path

from langgraph.checkpoint.serde.jsonplus import (
    JsonPlusSerializer,
)
from langgraph.checkpoint.sqlite import SqliteSaver


ALLOWED_MSGPACK_MODULES = [
    (
        "schemas.analysis_request",
        "AnalysisRequest",
    ),
    (
        "analysis.gex_calculation",
        "ContractGEX",
    ),
    (
        "schemas.gex_result",
        "GEXAnalysisResult",
    ),
    (
        "schemas.dex_result",
        "DEXResult",
    ),
    (
        "schemas.option_contract",
        "OptionContract",
    ),
    (
        "schemas.oi_result",
        "OIAnalysisResult",
    ),
    (
        "schemas.max_pain_result",
        "MaxPainResult",
    ),
    (
        "schemas.analysis_result",
        "AnalysisResult",
    ),
]


def create_sqlite_checkpointer(
    database_path: str | Path,
) -> tuple[SqliteSaver, sqlite3.Connection]:

    path = Path(database_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serializer = JsonPlusSerializer(
        allowed_msgpack_modules=(
            ALLOWED_MSGPACK_MODULES
        )
    )

    connection = sqlite3.connect(
        str(path),
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(
        connection,
        serde=serializer,
    )

    return checkpointer, connection