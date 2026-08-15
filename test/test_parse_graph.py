import os

from dotenv import load_dotenv

from agent.llm_agent import LLMAgent
from core.runtime import Runtime
from graph.option_graph import build_option_graph


load_dotenv()


def main():

    api_key = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found. "
            "Please check your .env file."
        )

    runtime = Runtime()

    agent = LLMAgent(
        runtime=runtime,
        api_key=api_key
    )

    graph = build_option_graph(
        agent
    )

    user_input = input("请输入：")

    result = graph.invoke(
        {
            "user_input": user_input
        }
    )

    request = result["request"]

    print("\n========== PARSED REQUEST ==========")
    print(f"Ticker: {request.ticker}")
    print(f"Expiration: {request.expiration}")
    print(f"Analysis types: {request.analysis_types}")
    print(f"Validation error: {result.get('validation_error')}")

    analysis_result = result["analysis_result"]

    print("\n========== ANALYSIS RESULT ==========")
    print(f"Ticker: {analysis_result.ticker}")
    print(f"Expiration: {analysis_result.expiration}")
    print(
        "GEX result present: "
        f"{analysis_result.gex_result is not None}"
    )
    print(
        "DEX result present: "
        f"{analysis_result.dex_result is not None}"
    )
    print(
        "OI result present: "
        f"{analysis_result.oi_result is not None}"
    )
    print(
        "Max Pain result present: "
        f"{analysis_result.maxpain_result is not None}"
    )

    print("\n========== ANALYSIS CONTEXT ==========")
    print(result["analysis_context"])

    print("\n========== FINAL ANSWER ==========")
    print(result["final_answer"])

if __name__ == "__main__":
    main()