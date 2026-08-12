import os

from dotenv import load_dotenv

from core.runtime import Runtime

from agent.llm_agent import LLMAgent



# ==========================
# Load .env
# ==========================

load_dotenv()



def main():


    # ==========================
    # 1. 检查 API Key
    # ==========================

    api_key = os.getenv(
        "DEEPSEEK_API_KEY"
    )


    if not api_key:

        raise ValueError(
            "DEEPSEEK_API_KEY not found. "
            "Please check your .env file."
        )



    # ==========================
    # 2. 初始化 Runtime
    # ==========================

    runtime = Runtime()



    # ==========================
    # 3. 初始化 Agent
    # ==========================

    agent = LLMAgent(

        runtime=runtime,

        api_key=api_key

    )



    # ==========================
    # 4. 用户输入
    # ==========================

    



    print(
        "\n========== USER =========="
    )
    user_input = input("请输入：")



    # ==========================
    # 5. Agent运行
    # ==========================

    answer = agent.run(
        user_input
    )



    # ==========================
    # 6. 输出结果
    # ==========================

    print(
        "\n========== AGENT ANSWER =========="
    )


    print(
        answer
    )



if __name__ == "__main__":

    main()