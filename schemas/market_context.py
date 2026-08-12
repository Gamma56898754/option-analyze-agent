from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketContext:
    """
    Runtime context for market analysis.

    Provides current market time information
    required for date calculation.
    """


    current_time: datetime


    timezone: str