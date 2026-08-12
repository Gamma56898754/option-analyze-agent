from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool



def main():

    ticker = "TSLA"


    print("\n========== Start Test ==========\n")


    # ==========================
    # 1. Get Cookies
    # ==========================

    browser = BrowserSession()

    cookies = browser.get_cookies(
        ticker
    )


    print(
        "Cookies loaded:",
        len(cookies)
    )


    # ==========================
    # 2. Create Client
    # ==========================

    client = OptionChartClient(
        cookies
    )


    # ==========================
    # 3. Get Expiration HTML
    # ==========================

    html = client.get_expiration_overview(
        ticker
    )


    print(
        "HTML received:",
        len(html)
    )


    # ==========================
    # 4. Get Market Context
    # ==========================

    market_time_tool = MarketTimeTool()


    market_context = (
        market_time_tool
        .get_market_context()
    )


    print("\n========== Market Context ==========")

    print(
        market_context
    )


    # ==========================
    # 5. Resolve Expiration
    # ==========================

    resolver = ExpirationResolver()


    results = resolver.resolve(
        html,
        market_context
    )


    # ==========================
    # 6. Print Result
    # ==========================

    print(
        "\n========== Expiration Result =========="
    )


    print(
        "Total expirations:",
        len(results)
    )


    for item in sorted(
        results,
        key=lambda x: x.expiration_date
    ):

        print(
            item
        )


    # ==========================
    # 7. Find Example
    # ==========================

    target = "2026-08-21"


    result = resolver.find(
        results,
        target
    )


    print(
        "\n========== Find Test =========="
    )


    if result:

        print(
            "Found:",
            result
        )

    else:

        print(
            "Not found:",
            target
        )



if __name__ == "__main__":

    main()