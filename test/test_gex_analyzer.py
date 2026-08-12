from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from analysis.gex_calculation import GEXCalculator
from analysis.gex_analyzer import GEXAnalyzer
from schemas.gex_result import GEXAnalysisResult


def main():

    ticker = "TSLA"

    target_expiration = "2026-08-19"



    print(
        "\n========== START GEX ANALYZER TEST ==========\n"
    )


    # ==========================
    # 1. Browser
    # ==========================

    browser = BrowserSession()


    cookies = browser.get_cookies(
        ticker
    )



    # ==========================
    # 2. Client
    # ==========================

    client = OptionChartClient(
        cookies
    )



    # ==========================
    # 3. Expiration Resolver
    # ==========================

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



    # ==========================
    # 4. Option Chain
    # ==========================

    html = client.get_option_chain(

        ticker,

        expiration_info.expiration_date,

        expiration_info.expiration_type

    )



    # ==========================
    # 5. Parser
    # ==========================

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



    # ==========================
    # 6. Contract GEX
    # ==========================

    calculator = GEXCalculator()


    gex_list = calculator.calculate(

        contracts,

        price

    )


    print(
        "Contract GEX count:",
        len(gex_list)
    )



    # ==========================
    # 7. GEX Analyzer
    # ==========================

    analyzer = GEXAnalyzer()


    result = analyzer.analyze(
        gex_list
    )



    # ==========================
    # 8. Output
    # ==========================

    print(
        "\n========== GEX Summary ==========\n"
    )


    print(
        "Total GEX:",
        result.total_gex
    )


    print(
        "Call GEX:",
        result.call_gex
    )


    print(
        "Put GEX:",
        result.put_gex
    )



    print(
        "\n========== CALL TOP 3 ==========\n"
    )


    print(result.call_top_gex)
    print(result.call_2nd_top_gex)
    print(result.call_3rd_top_gex)



    print(
        "\n========== PUT TOP 3 ==========\n"
    )


    print(result.put_top_gex)
    print(result.put_2nd_top_gex)
    print(result.put_3rd_top_gex)



    # ==========================
    # 9. Validation
    # ==========================

    assert result.call_top_gex is not None

    assert result.put_top_gex is not None


    assert result.call_gex > 0

    assert result.put_gex < 0


    assert (
        result.total_gex
        ==
        result.call_gex + result.put_gex
    )


    print(
        "\nGEX Analyzer test passed!"
    )



if __name__ == "__main__":

    main()