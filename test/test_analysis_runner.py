from core.runtime import Runtime
from core.analysis_runner import AnalysisRunner

from schemas.analysis_request import AnalysisRequest



def print_result(
    name,
    result
):

    print("\n===================")
    print(name)
    print("===================")


    print(
        "Ticker:",
        result.ticker
    )


    print(
        "Expiration:",
        result.expiration
    )


    print(
        "GEX:",
        result.gex_result is not None
    )


    print(
        "DEX:",
        result.dex_result is not None
    )


    print(
        "OI:",
        result.oi_result is not None
    )


    print(
        "MaxPain:",
        result.maxpain_result is not None
    )



def main():

    # Runtime只创建一次
    runtime = Runtime()


    runner = AnalysisRunner(
        runtime
    )


    # ==========================
    # Case 1
    # TSLA 8.10 GEX
    # ==========================

    request1 = AnalysisRequest(

        ticker="TSLA",

        expiration="2026-08-10",

        analysis_types=[
            "gex"
        ]

    )


    result1 = runner.run(
        request1
    )


    print_result(
        "TSLA GEX",
        result1
    )



    # ==========================
    # Case 2
    # NVDA 8.21 DEX
    # ==========================

    request2 = AnalysisRequest(

        ticker="NVDA",

        expiration="2026-08-21",

        analysis_types=[
            "dex"
        ]

    )


    result2 = runner.run(
        request2
    )


    print_result(
        "NVDA DEX",
        result2
    )



    # ==========================
    # Case 3
    # TSLA 全分析
    # ==========================

    request3 = AnalysisRequest(

        ticker="TSLA",

        expiration="2026-08-21",

        analysis_types=[
            "gex",
            "dex",
            "oi",
            "maxpain"
        ]

    )


    result3 = runner.run(
        request3
    )


    print_result(
        "TSLA FULL",
        result3
    )



if __name__ == "__main__":
    main()