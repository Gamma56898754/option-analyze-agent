import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from agent.tool_schemas import OPTION_ANALYSIS_TOOLS


def main():

    load_dotenv()

    api_key = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "DEEPSEEK_API_KEY not found. "
            "Please check your .env file."
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "user",
                "content": (
                    "Call run_option_analysis exactly once to analyze "
                    "TSLA options expiring on 2026-08-21 for GEX. "
                    "Do not provide a normal text answer."
                ),
            }
        ],
        tools=OPTION_ANALYSIS_TOOLS,
    )

    message = response.choices[0].message

    if not message.tool_calls:
        raise AssertionError(
            f"Expected a tool call, got content: {message.content}"
        )

    tool_call = message.tool_calls[0]

    assert tool_call.function.name == (
        "run_option_analysis"
    )

    arguments = json.loads(
        tool_call.function.arguments
    )

    assert arguments["ticker"] == "TSLA"

    assert arguments["expiration"] == "2026-08-21"

    assert arguments["analysis_types"] == [
        "gex"
    ]

    print("DeepSeek tool call smoke test passed.")
    print("Tool name:", tool_call.function.name)
    print("Arguments:", arguments)


if __name__ == "__main__":

    main()