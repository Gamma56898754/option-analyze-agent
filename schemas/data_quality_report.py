from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class DataQualityReport:
    """Provenance and observable quality facts for one analysis run."""

    source: str
    fetched_at: datetime
    cache_state: Literal["hit", "miss", "bypass"]
    contract_count: int
    warnings: list[str] = field(default_factory=list)
