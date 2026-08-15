from datetime import date

from tools.natural_date_resolver import (
    NaturalDateResolver,
)


def main():

    resolver = NaturalDateResolver()

    market_date = date(
        2026,
        8,
        17,
    )

    assert (
        resolver.resolve(
            "analyze TSLA today",
            market_date,
        )
        == "2026-08-17"
    )

    assert (
        resolver.resolve(
            "分析 TSLA 明天的 DEX",
            market_date,
        )
        == "2026-08-18"
    )

    assert (
        resolver.resolve(
            "analyze TSLA this Friday",
            market_date,
        )
        == "2026-08-21"
    )

    assert (
        resolver.resolve(
            "分析 TSLA 下周五的 OI",
            market_date,
        )
        == "2026-08-28"
    )

    assert (
        resolver.resolve(
            "analyze TSLA 2026-08-21 GEX",
            market_date,
        )
        is None
    )

    print(
        "NaturalDateResolver test passed."
    )


if __name__ == "__main__":
    main()