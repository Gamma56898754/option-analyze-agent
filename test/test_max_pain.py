from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from analysis.max_pain_analyzer import MaxPainAnalyzer



def main():

    ticker = "TSLA"

    target_expiration = "2026-08-10"



    print(
        "\n========== START MAX PAIN TEST ==========\n"
    )


    # =================================
    # 1. Browser Session
    # =================================

    browser = BrowserSession()


    cookies = browser.get_cookies(
        ticker
    )



    # =================================
    # 2. Client
    # =================================

    client = OptionChartClient(
        cookies
    )



    # =================================
    # 3. Resolve expiration
    # =================================

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


    expiration_list = resolver.resolve(

        expiration_html,

        market_context

    )


    expiration_info = resolver.find(

        expiration_list,

        target_expiration

    )


    if expiration_info is None:

        raise Exception(
            f"Expiration not found: {target_expiration}"
        )



    print(
        "\n========== EXPIRATION INFO =========="
    )

    print(
        expiration_info
    )



    # =================================
    # 4. Get correct option chain
    # =================================

    html = client.get_option_chain(

        ticker,

        expiration_info.expiration_date,

        expiration_info.expiration_type

    )



    # =================================
    # 5. Parse contracts
    # =================================

    parser = OptionChainParser()


    contracts = parser.parse(

        html,

        ticker,

        expiration_info.expiration_date

    )


    print(
        "\nContracts:",
        len(contracts)
    )



    # =================================
    # 6. Parse underlying price
    # =================================

    current_price = (
        parser
        .parse_underlying_price(
            html
        )
    )


    print(
        "Underlying Price:",
        current_price
    )



    # =================================
    # 7. Max Pain Analyze
    # =================================

    analyzer = MaxPainAnalyzer()


    result = analyzer.analyze(

        contracts,

        current_price

    )



    # =================================
    # 8. Output
    # =================================

    print(
        "\n========== MAX PAIN RESULT ==========\n"
    )


    print(
        "Current Price:",
        result.current_price
    )


    print(
        "Max Pain Price:",
        result.max_pain_price
    )


    print(
        "Total Loss:",
        result.total_loss
    )


    print(
        "Distance Percent:",
        result.distance_percent
    )


    print(
        "\n========== TEST FINISHED =========="
    )



if __name__ == "__main__":

    main()