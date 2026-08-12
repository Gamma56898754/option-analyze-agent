from data.browser_session import BrowserSession
from data.optionchart_client import OptionChartClient
from data.parser import OptionChainParser



def main():

    ticker = "TSLA"

    expiration = "2026-08-14"


    # ======================
    # Step 1
    # 获取浏览器cookie
    # ======================

    browser = BrowserSession()


    cookies = browser.get_cookies(
        ticker
    )


    print(
        "Cookie obtained:",
        len(cookies)
    )


    



    # ======================
    # Step 2
    # 请求OptionChain
    # ======================

    client = OptionChartClient(
        cookies
    )


    html = client.get_option_chain(

        ticker,

        expiration

    )


    print(
        "HTML length:",
        len(html)
    )



    # ======================
    # Step 3
    # Parser
    # ======================


    parser = OptionChainParser()


    contracts = parser.parse(

        html,

        ticker,

        expiration

    )



    print(
        "Contract count:",
        len(contracts)
    )



    # ======================
    # Step 4
    # 查看结果
    # ======================

    for contract in contracts:

        if contract.strike == 330:

            print(contract)

    underlying_price = parser.parse_underlying_price(
    html
    )
    print(underlying_price)

if __name__ == "__main__":

    main()