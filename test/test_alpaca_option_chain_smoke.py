import os
from collections import Counter

import requests
from dotenv import load_dotenv


BASE_URL = (
    "https://data.alpaca.markets"
)


def main() -> None:

    load_dotenv()

    api_key = os.getenv(
        "ALPACA_API_KEY"
    )

    secret_key = os.getenv(
        "ALPACA_SECRET_KEY"
    )

    if not api_key or not secret_key:
        raise ValueError(
            "ALPACA_API_KEY or "
            "ALPACA_SECRET_KEY not found."
        )

    ticker = "TSLA"

    url = (
        f"{BASE_URL}"
        f"/v1beta1/options/snapshots/{ticker}"
    )

    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }

    params = {
        "feed": "indicative",
        "limit": 100,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15,
    )

    print("Status:", response.status_code)

    if not response.ok:
        print(
            "Response body:",
            response.text[:1000],
        )

        response.raise_for_status()

    payload = response.json()

    print(
        "Top-level keys:",
        list(payload.keys()),
    )

    snapshots = payload.get(
        "snapshots",
        {},
    )

    print(
        "Snapshot count:",
        len(snapshots),
    )

    field_counts = Counter()

    greeks_count = 0
    iv_count = 0
    trade_count = 0

    example_with_greeks = None

    for symbol, snapshot in snapshots.items():

        field_counts.update(
            snapshot.keys()
        )

        if snapshot.get("greeks") is not None:
            greeks_count += 1

            if example_with_greeks is None:
                example_with_greeks = (
                    symbol,
                    snapshot,
                )

        if snapshot.get(
            "impliedVolatility"
        ) is not None:
            iv_count += 1

        if snapshot.get(
            "latestTrade"
        ) is not None:
            trade_count += 1

    print(
        "Snapshot field counts:",
        dict(field_counts),
    )

    print(
        "Contracts with Greeks:",
        greeks_count,
    )

    print(
        "Contracts with implied volatility:",
        iv_count,
    )

    print(
        "Contracts with latest trade:",
        trade_count,
    )

    if example_with_greeks is not None:

        symbol, snapshot = example_with_greeks

        print(
            "Example symbol with Greeks:",
            symbol,
        )

        print(
            "Greeks:",
            snapshot["greeks"],
        )

    else:

        print(
            "No Greeks found in this response."
        )

    print(
        "Alpaca option-chain smoke "
        "test passed."
    )


if __name__ == "__main__":
    main()