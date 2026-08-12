from core.runtime import Runtime

from tools.option_chain_tool import OptionChainTool
from tools.max_pain_tool import MaxPainTool



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
    # 3. 初始化 Max Pain Tool
    # ==========================

    max_pain_tool = MaxPainTool()


    # ==========================
    # 4. Max Pain分析
    # ==========================

    max_pain_result = (
        max_pain_tool.run(
            option_chain_result
        )
    )


    # ==========================
    # 5. 输出结果
    # ==========================

    print("\n========== MAX PAIN RESULT ==========")


    print(
        "Max Pain Price:",
        max_pain_result.max_pain_price
    )


    print(
        "Total Loss:",
        max_pain_result.total_loss
    )


    print(
        "Current Price:",
        max_pain_result.current_price
    )


    print(
        "Distance Percent:",
        max_pain_result.distance_percent,
        "%"
    )


    print(
        "\nMax Pain Tool test success!"
    )



if __name__ == "__main__":
    main()