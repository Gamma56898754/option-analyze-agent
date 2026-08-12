from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from analysis.gex_calculation import GEXCalculator



def main():

    ticker = "TSLA"

    target_expiration = "2026-08-10"



    print(
        "\n========== START GEX CALCULATION TEST ==========\n"
    )


    # =========================
    # 1. Browser
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
    # 3. Resolve expiration
    # =========================

    expiration_html = (
        client
        .get_expiration_overview(
            ticker
        )
    )


    market_context = (
        MarketTimeTool()
        .get_market_context()
    )


    resolver = ExpirationResolver()


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
            f"Expiration not found: {target_expiration}"
        )


    print(
        "\nExpiration Info:"
    )

    print(
        expiration_info
    )



    # =========================
    # 4. Get correct chain
    # =========================

    html = client.get_option_chain(

        ticker,

        expiration_info.expiration_date,

        expiration_info.expiration_type

    )


    print(
        "HTML length:",
        len(html)
    )



    # =========================
    # 5. Parser
    # =========================

    parser = OptionChainParser()


    contracts = parser.parse(

        html,

        ticker,

        expiration_info.expiration_date

    )


    price = parser.parse_underlying_price(
        html
    )


    print(
        "Underlying price:",
        price
    )


    print(
        "Contracts:",
        len(contracts)
    )



    # =========================
    # 6. GEX Calculate
    # =========================

    calculator = GEXCalculator()


    gex_results = calculator.calculate(

        contracts,

        price

    )



    print(
        "\nGEX Result Sample:\n"
    )


    for item in gex_results[:20]:

        print(item)



    print(
        "\nTotal contracts with GEX:",
        len(gex_results)
    )



if __name__ == "__main__":

    main()