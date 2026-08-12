from dataclasses import dataclass

from schemas.option_contract import OptionContract


@dataclass
class OIAnalysisResult:
    """
    Result of option open interest analysis.

    Contains:
    - DTE information
    - selected strike range
    - highest OI contracts
    - top OI contracts within range
    """


    # Days to expiration
    dte: int


    # Selected strike range percentage
    strike_range_percent: float


    # Highest OI in entire option chain
    call_max_oi: OptionContract

    put_max_oi: OptionContract


    # Top 3 OI contracts within price range
    call_top_oi: list[OptionContract]

    put_top_oi: list[OptionContract]