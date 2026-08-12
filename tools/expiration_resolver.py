import re
from dataclasses import dataclass
from datetime import datetime, date

from schemas.market_context import MarketContext
from schemas.expiration_info import ExpirationInfo


class ExpirationResolver:
    """
    Resolve expiration metadata from OptionCharts HTML
    """



    def resolve(
        self,
        html: str,
        market_context: MarketContext
    ) -> list[ExpirationInfo]:
        """
        Parse expiration information.

        market_context provides
        current US market date.
        """


        expiration_pairs = self.extract_expirations(
            html
        )


        results = []


        for expiration_date, expiration_type in expiration_pairs:


            dte = self.calculate_dte(
                expiration_date,
                market_context
            )


            results.append(
                ExpirationInfo(

                    expiration_date=expiration_date,

                    expiration_type=expiration_type,

                    dte=dte

                )
            )


        return results



    def extract_expirations(
        self,
        html: str
    ) -> set[tuple[str, str]]:
        """
        Extract:

        2026-08-21:m
        """


        pattern = (
            r"expiration_dates="
            r"(\d{4}-\d{2}-\d{2})"
            r"(?:\:|%3A)"
            r"([wm])"
        )


        matches = re.findall(
            pattern,
            html
        )


        return set(matches)



    def calculate_dte(
        self,
        expiration_date: str,
        market_context: MarketContext
    ) -> int:
        """
        Calculate DTE using US market date.

        Do NOT use local machine date.
        """


        expiration = datetime.strptime(
            expiration_date,
            "%Y-%m-%d"
        ).date()


        current_date = (
            market_context.current_time
            .date()
        )


        return (
            expiration - current_date
        ).days



    def find(
        self,
        expirations: list[ExpirationInfo],
        target_date: str
    ) -> ExpirationInfo | None:


        for item in expirations:

            if item.expiration_date == target_date:

                return item


        return None