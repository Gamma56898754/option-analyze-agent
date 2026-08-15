from dataclasses import dataclass


@dataclass
class AnalysisRequest:

    ticker: str

    expiration: str

    analysis_types: list[str]

    execution_mode: str = "run_analysis"

    force_refresh: bool = False