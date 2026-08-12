from core.runtime import Runtime

from tools.option_chain_tool import OptionChainTool
from tools.gex_tool import GEXTool



def main():

    # ==========================
    # 1. 初始化Runtime
    # ==========================

    runtime = Runtime()


    # ==========================
    # 2. 创建OptionChain Tool
    # ==========================

    option_chain_tool = OptionChainTool(
        runtime
    )


    # ==========================
    # 3. 获取OptionChainResult
    # ==========================

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
    # 4. 创建GEX Tool
    # ==========================

    gex_tool = GEXTool()


    # ==========================
    # 5. GEX分析
    # ==========================

    gex_result = (
        gex_tool.run(
            option_chain_result
        )
    )


    print("\n========== GEX RESULT ==========")


    print(
        "Total GEX:",
        gex_result.total_gex
    )


    print(
        "Call GEX:",
        gex_result.call_gex
    )


    print(
        "Put GEX:",
        gex_result.put_gex
    )


    print("\n----- CALL TOP -----")


    print(
        gex_result.call_top_gex
    )


    print(
        gex_result.call_2nd_top_gex
    )


    print(
        gex_result.call_3rd_top_gex
    )


    print("\n----- PUT TOP -----")


    print(
        gex_result.put_top_gex
    )


    print(
        gex_result.put_2nd_top_gex
    )


    print(
        gex_result.put_3rd_top_gex
    )


    print(
        "\nGEX Tool test success!"
    )



if __name__ == "__main__":
    main()