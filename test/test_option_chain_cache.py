from datetime import datetime, timedelta, timezone

from cache.option_chain_cache import OptionChainCache
from schemas.expiration_info import ExpirationInfo
from schemas.option_chain_result import OptionChainResult


def build_result() -> OptionChainResult:

    return OptionChainResult(
        ticker="TSLA",
        expiration_info=ExpirationInfo(
            expiration_date="2026-08-17",
            expiration_type="w",
            dte=2,
        ),
        underlying_price=341.64,
        contracts=[],
    )


def main():

    cache = OptionChainCache()

    result = build_result()

    cached_at = datetime(
        2026,
        8,
        15,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    cache.set(
        ticker="TSLA",
        expiration="2026-08-17",
        result=result,
        now=cached_at,
    )

    hit_result = cache.get(
        ticker="tsla",
        expiration="2026-08-17",
        now=cached_at + timedelta(
            minutes=4,
            seconds=59,
        ),
    )

    assert hit_result is result

    expired_result = cache.get(
        ticker="TSLA",
        expiration="2026-08-17",
        now=cached_at + timedelta(
            minutes=5,
        ),
    )

    assert expired_result is None

    print("OptionChainCache test passed.")


if __name__ == "__main__":
    main()