from core.runtime import Runtime
from tools.option_chain_tool import OptionChainTool



def main():

    runtime = Runtime()


    option_chain_tool = OptionChainTool(
        runtime
    )


    result = option_chain_tool.run(
        "TSLA",
        "2026-08-21"
    )
    result = option_chain_tool.run(
        "NVDA",
        "2026-08-10"
    )

    print(
        result.ticker
    )


if __name__ == "__main__":
    main()