from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from schemas.option_chain_result import OptionChainResult


@dataclass
class OptionChainCacheEntry:
    result: OptionChainResult
    cached_at: datetime


class OptionChainCache:
    """
    In-memory cache for parsed option-chain results.

    Cache key:
        ticker + expiration

    TTL:
        5 minutes
    """

    def __init__(
        self,
        ttl: timedelta = timedelta(minutes=5),
    ):
        self.ttl = ttl

        self._entries: dict[
            tuple[str, str],
            OptionChainCacheEntry
        ] = {}

    def get(
        self,
        ticker: str,
        expiration: str,
        now: datetime | None = None,
    ) -> OptionChainResult | None:

        key = (
            ticker.upper(),
            expiration,
        )

        entry = self._entries.get(
            key
        )

        if entry is None:
            return None

        current_time = now or datetime.now(
            timezone.utc
        )

        if current_time - entry.cached_at >= self.ttl:
            del self._entries[key]
            return None

        return entry.result

    def set(
        self,
        ticker: str,
        expiration: str,
        result: OptionChainResult,
        now: datetime | None = None,
    ) -> None:

        key = (
            ticker.upper(),
            expiration,
        )

        cached_at = now or datetime.now(
            timezone.utc
        )

        self._entries[key] = OptionChainCacheEntry(
            result=result,
            cached_at=cached_at,
        )