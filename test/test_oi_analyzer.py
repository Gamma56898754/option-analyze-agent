from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver

from analysis.oi_analyzer import OIAnalyzer



def main():

    ticker = "TSLA"

    target_expiration = "2026-08-21"


    print("\n========== START OI TEST ==========\n")



    # =========================
    # 1. Browser cookies
    # =========================

    browser = BrowserSession()


    cookies = browser.get_cookies(
        ticker
    )



    # =========================
    # 2. Client
    # =========================

    client = OptionChartClient(
        cookies
    )



    # =========================
    # 3. Get expiration metadata
    # =========================

    expiration_html = (
        client
        .get_expiration_overview(
            ticker
        )
    )


    resolver = ExpirationResolver()


    # 这里测试阶段暂时使用 MarketTimeTool
    # 如果你已有market_context获取方式替换即可

    from tools.market_time_tool import MarketTimeTool


    market_time_tool = MarketTimeTool()


    market_context = (
        market_time_tool
        .get_market_context()
    )


    expirations = resolver.resolve(
        expiration_html,
        market_context
    )



    expiration_info = resolver.find(
        expirations,
        target_expiration
    )


    if expiration_info is None:

        raise Exception(
            f"Cannot find expiration {target_expiration}"
        )


    print("\n========== Expiration Info ==========")

    print(
        expiration_info
    )



    # =========================
    # 4. Get correct option chain
    # =========================

    html = client.get_option_chain(

        ticker,

        expiration_info.expiration_date,

        expiration_info.expiration_type

    )



    # =========================
    # 5. Parse contracts
    # =========================

    parser = OptionChainParser()


    contracts = parser.parse(

        html,

        ticker,

        expiration_info.expiration_date

    )



    print("\nContracts:")

    print(
        len(contracts)
    )



    # =========================
    # 6. Underlying price
    # =========================

    underlying_price = (
        parser.parse_underlying_price(
            html
        )
    )


    print(
        "Underlying:",
        underlying_price
    )



    # =========================
    # 7. OI Analyzer
    # =========================

    analyzer = OIAnalyzer()



    result = analyzer.analyze(

        contracts,

        expiration_info,

        underlying_price

    )



    # =========================
    # 8. Output
    # =========================

    print(
        "\n========== OI RESULT =========="
    )


    print(
        "DTE:",
        result.dte
    )


    print(
        "Strike Range:",
        result.strike_range_percent
    )


    print(
        "\nCALL MAX OI:"
    )

    print(
        result.call_max_oi
    )


    print(
        "\nPUT MAX OI:"
    )

    print(
        result.put_max_oi
    )


    print(
        "\nCALL TOP 3:"
    )

    for item in result.call_top_oi:

        print(item)



    print(
        "\nPUT TOP 3:"
    )

    for item in result.put_top_oi:

        print(item)



    print(
        "\n========== TEST FINISHED =========="
    )



if __name__ == "__main__":

    main()