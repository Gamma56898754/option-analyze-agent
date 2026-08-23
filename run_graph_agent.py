import os

from dotenv import load_dotenv

from agent.llm_agent import LLMAgent
from core.runtime import Runtime
from graph.option_graph import build_option_graph

from pathlib import Path

from core.checkpoint_factory import (
    create_sqlite_checkpointer,
)


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

    runtime = Runtime()

    agent = LLMAgent(
        runtime=runtime,
        api_key=api_key
    )

    checkpointer, db_connection = (
        create_sqlite_checkpointer(
            Path("memory")
            / "option_agent_checkpoints.db"
        )
    )

    graph = build_option_graph(
        agent,
        checkpointer=checkpointer,
    )

    print("\n========== OPTION ANALYZE AGENT ==========")
    print("推荐日期格式：YYYY-MM-DD")
    print("输入 exit、quit 或 退出 可结束程序。")

    config = {
        "configurable": {
        "thread_id": "local-option-session"#local-option-session 为本地对话 其他为测试
        }
    }

    while True:

        user_input = input("\n请输入：").strip()

        if user_input.lower() in {
            "exit",
            "quit",
            "退出"
        }:
            print("Agent 已退出。")
            break

        if not user_input:
            print("请输入有效问题。")
            continue

        try:
            result = graph.invoke(
                {
                    "user_input": user_input
                },
                config = config,
            )

            print("\n========== AGENT ANSWER ==========")
            print(result["final_answer"])

        except Exception as exc:
            print("\n========== SYSTEM ERROR ==========")
            print(exc)

    db_connection.close()

if __name__ == "__main__":
    main()