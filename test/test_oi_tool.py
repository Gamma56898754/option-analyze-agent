from core.runtime import Runtime

from tools.option_chain_tool import OptionChainTool
from tools.oi_tool import OITool



def main():

    # ==========================
    # 1. 初始化 Runtime
    # ==========================

    runtime = Runtime()


    # ==========================
    # 2. 获取 OptionChainResult
    # ==========================

    option_chain_tool = OptionChainTool(
        runtime
    )


    option_chain_result = (
        option_chain_tool.run(
            ticker="TSLA",
            expiration_date="2026-08-21"
        )
    )


    print("\n========== OPTION CHAIN ==========")


    print(
        "Ticker:",
        option_chain_result.ticker
    )


    print(
        "Underlying Price:",
        option_chain_result.underlying_price
    )


    print(
        "Contracts:",
        len(option_chain_result.contracts)
    )


    print(
        "DTE:",
        option_chain_result.expiration_info.dte
    )


    # ==========================
    # 3. OI Tool
    # ==========================

    oi_tool = OITool()


    oi_result = (
        oi_tool.run(
            option_chain_result
        )
    )


    # ==========================
    # 4. 输出结果
    # ==========================

    print("\n========== OI RESULT ==========")


    print(
        "DTE:",
        oi_result.dte
    )


    print(
        "Strike Range:",
        oi_result.strike_range_percent
    )


    print("\n----- CALL MAX OI -----")

    print(
        oi_result.call_max_oi
    )


    print("\n----- PUT MAX OI -----")

    print(
        oi_result.put_max_oi
    )


    print("\n----- CALL TOP OI -----")

    for contract in oi_result.call_top_oi:

        print(
            contract.contract_symbol,
            "Strike:",
            contract.strike,
            "OI:",
            contract.open_interest
        )


    print("\n----- PUT TOP OI -----")

    for contract in oi_result.put_top_oi:

        print(
            contract.contract_symbol,
            "Strike:",
            contract.strike,
            "OI:",
            contract.open_interest
        )


    print(
        "\nOI Tool test success!"
    )



if __name__ == "__main__":
    main()