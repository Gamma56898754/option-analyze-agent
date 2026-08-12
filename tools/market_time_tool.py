from datetime import datetime
from zoneinfo import ZoneInfo

from schemas.market_context import MarketContext



class MarketTimeTool:
    """
    Tool for getting current US market time.

    Responsibility:

        Get current datetime
        Provide timezone


    Does NOT:

        - judge market status
        - calculate DTE
        - analyze options
    """


    MARKET_TIMEZONE = "America/New_York"



    def get_market_context(
        self
    ) -> MarketContext:
        """
        Return current market time context.
        """


        now = datetime.now(
            ZoneInfo(
                self.MARKET_TIMEZONE
            )
        )


        return MarketContext(

            current_time=now,

            timezone=self.MARKET_TIMEZONE

        )