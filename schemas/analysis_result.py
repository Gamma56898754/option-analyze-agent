from dataclasses import dataclass
from schemas.gex_result import GEXAnalysisResult
from schemas.dex_result import DEXResult
from schemas.oi_result import OIAnalysisResult
from schemas.max_pain_result import MaxPainResult    

@dataclass
class AnalysisResult:

    ticker: str

    expiration: str

    gex_result: GEXAnalysisResult | None = None

    dex_result: DEXResult | None = None

    oi_result: OIAnalysisResult | None = None

    maxpain_result: MaxPainResult | None = None