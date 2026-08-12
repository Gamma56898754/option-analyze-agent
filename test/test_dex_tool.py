from core.runtime import Runtime

from tools.option_chain_tool import OptionChainTool
from tools.dex_tool import DEXTool



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


    # ==========================
    # 3. 初始化 DEX Tool
    # ==========================

    dex_tool = DEXTool()


    # ==========================
    # 4. DEX分析
    # ==========================

    dex_result = (
        dex_tool.run(
            option_chain_result
        )
    )


    print("\n========== DEX RESULT ==========")


    print(
        "Call DEX:",
        dex_result.call_dex
    )


    print(
        "Put DEX:",
        dex_result.put_dex
    )


    print(
        "Total DEX:",
        dex_result.total_dex
    )


    print(
        "\nDEX Tool test success!"
    )



if __name__ == "__main__":
    main()