from dataclasses import dataclass


@dataclass
class AnalysisRequest:

    ticker: str

    expiration: str

    analysis_types: list[str]