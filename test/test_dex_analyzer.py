from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser

from tools.expiration_resolver import ExpirationResolver
from tools.market_time_tool import MarketTimeTool

from analysis.dex_analyzer import DEXAnalyzer



def main():

    ticker = "TSLA"

    target_expiration = "2026-08-21"



    print(
        "\n========== START DEX TEST ==========\n"
    )



    # ==========================
    # 1. Browser Session
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
    # 3. Resolve expiration
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
        "\n========== EXPIRATION INFO =========="
    )


    print(
        expiration_info
    )



    # ==========================
    # 4. Get correct option chain
    # ==========================

    html = client.get_option_chain(

        ticker,

        expiration_info.expiration_date,

        expiration_info.expiration_type

    )



    print(
        "\nHTML length:",
        len(html)
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



    print(
        "\nContracts:",
        len(contracts)
    )



    # ==========================
    # 6. DEX Analyzer
    # ==========================

    analyzer = DEXAnalyzer()


    result = analyzer.analyze(
        contracts
    )



    # ==========================
    # 7. Output
    # ==========================

    print(
        "\n========== DEX RESULT ==========\n"
    )


    print(
        "Call DEX:",
        result.call_dex
    )


    print(
        "Put DEX:",
        result.put_dex
    )


    print(
        "Total DEX:",
        result.total_dex
    )



    # ==========================
    # 8. Basic Validation
    # ==========================

    print(
        "\n========== VALIDATION =========="
    )


    assert result.call_dex > 0, (
        "CALL DEX should be positive"
    )


    assert result.put_dex < 0, (
        "PUT DEX should be negative"
    )


    assert (
        result.total_dex
        ==
        result.call_dex
        +
        result.put_dex
    ), (
        "Total DEX calculation error"
    )



    print(
        "\nDEX Analyzer test passed!"
    )



if __name__ == "__main__":

    main()