import re

from datetime import date, timedelta


class NaturalDateResolver:
    """
    Resolve supported natural-language date expressions
    using the US market date.
    """

    FRIDAY = 4

    def resolve(
        self,
        user_input: str,
        market_date: date,
    ) -> str | None:

        text = user_input.lower()

        if (
            "today" in text
            or "今天" in user_input
        ):
            return market_date.isoformat()

        if (
            "tomorrow" in text
            or "明天" in user_input
        ):
            return (
                market_date
                + timedelta(days=1)
            ).isoformat()

        if (
            re.search(
                r"\bthis\s+friday\b",
                text,
            )
            or "本周五" in user_input
        ):
            return self._next_friday(
                market_date
            ).isoformat()

        if (
            re.search(
                r"\bnext\s+friday\b",
                text,
            )
            or "下周五" in user_input
        ):
            return self._next_week_friday(
                market_date
            ).isoformat()

        return None

    def _next_friday(
        self,
        market_date: date,
    ) -> date:

        days_until_friday = (
            self.FRIDAY
            - market_date.weekday()
        ) % 7

        return market_date + timedelta(
            days=days_until_friday
        )

    def _next_week_friday(
        self,
        market_date: date,
    ) -> date:

        days_until_next_monday = (
            7 - market_date.weekday()
        )

        next_monday = market_date + timedelta(
            days=days_until_next_monday
        )

        return next_monday + timedelta(
            days=self.FRIDAY
        )