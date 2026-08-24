from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from schemas.option_chain_result import OptionChainResult


CACHE_TTL_SECONDS = 300

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
        ttl: timedelta | None = None,
    ):
        self.ttl = (
            ttl
            if ttl is not None
            else timedelta(
                seconds=CACHE_TTL_SECONDS
            )
        )

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

        entry = self.get_entry(
            ticker=ticker,
            expiration=expiration,
            now=now,
        )

        if entry is None:
            return None

        return entry.result

    def get_entry(
        self,
        ticker: str,
        expiration: str,
        now: datetime | None = None,
    ) -> OptionChainCacheEntry | None:
        """Return a valid cache entry when callers need its fetch timestamp."""

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

        return entry

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
