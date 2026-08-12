from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class OptionContract:
    """
    Standard representation of one option contract.

    This class only stores structured option data.
    It does NOT:
    - fetch data
    - parse HTML
    - calculate GEX
    """


    # =====================
    # Contract Identity
    # =====================

    ticker: str

    contract_symbol: str

    expiration: str
    """
    Expiration date.

    Example:
    2026-08-10
    """


    option_type: Literal["CALL", "PUT"]


    strike: float



    # =====================
    # Market Data
    # =====================

    last: Optional[float] = None

    bid: Optional[float] = None

    mid: Optional[float] = None

    ask: Optional[float] = None


    volume: Optional[int] = None

    open_interest: Optional[int] = None



    # =====================
    # Greeks
    # =====================

    implied_volatility: Optional[float] = None

    delta: Optional[float] = None

    gamma: Optional[float] = None

    theta: Optional[float] = None

    vega: Optional[float] = None