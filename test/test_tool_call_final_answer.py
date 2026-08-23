from types import SimpleNamespace

from agent.llm_agent import LLMAgent


class FakeCompletions:

    def __init__(self):
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="这是基于工具结果生成的分析。"
                    )
                )
            ]
        )


class FakeClient:

    def __init__(self):
        self.chat = SimpleNamespace(
            completions=FakeCompletions()
        )


def test_generate_answer_after_tool_call():

    agent = LLMAgent.__new__(LLMAgent)
    agent.client = FakeClient()

    decision = {
        "decision_type": "tool_call",
        "tool_call_id": "call_test_001",
        "tool_name": "run_option_analysis",
        "arguments_json": (
            '{"ticker":"TSLA","expiration":"2026-08-21",'
            '"analysis_types":["gex"]}'
        ),
    }

    answer = agent.generate_answer_after_tool_call(
        user_input="分析 TSLA 的 GEX",
        decision=decision,
        analysis_context="Total GEX: 100.0",
    )

    assert answer == "这是基于工具结果生成的分析。"

    messages = agent.client.chat.completions.last_kwargs[
        "messages"
    ]

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    assert messages[2]["role"] == "assistant"
    assert messages[2]["tool_calls"][0]["id"] == (
        "call_test_001"
    )

    assert messages[3]["role"] == "tool"
    assert messages[3]["tool_call_id"] == "call_test_001"
    assert messages[3]["content"] == "Total GEX: 100.0"

    print("Tool-call final answer protocol test passed.")


if __name__ == "__main__":
    test_generate_answer_after_tool_call()