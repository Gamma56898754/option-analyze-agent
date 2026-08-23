from types import SimpleNamespace

from agent.llm_agent import LLMAgent


class FakeCompletions:

    def __init__(self, response):

        self.response = response

        self.kwargs = None

    def create(self, **kwargs):

        self.kwargs = kwargs

        return self.response


class FakeClient:

    def __init__(self, response):

        self.chat = SimpleNamespace(
            completions=FakeCompletions(
                response
            )
        )


def test_decide_next_action_returns_tool_call():

    tool_call = SimpleNamespace(
        id="call_test_001",
        function=SimpleNamespace(
            name="run_option_analysis",
            arguments=(
                '{"ticker":"TSLA",'
                '"expiration":"2026-08-21",'
                '"analysis_types":["gex"]}'
            ),
        ),
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=[tool_call],
                    content=None,
                )
            )
        ]
    )

    agent = LLMAgent.__new__(
        LLMAgent
    )

    agent.client = FakeClient(
        response
    )

    agent.tool_schemas = [
        {
            "type": "function",
        }
    ]

    decision = agent.decide_next_action(
        user_input=(
            "Analyze TSLA GEX for 2026-08-21"
        ),
        market_date="2026-08-17",
    )

    assert decision["decision_type"] == (
        "tool_call"
    )

    assert decision["tool_call_id"] == (
        "call_test_001"
    )

    assert decision["tool_name"] == (
        "run_option_analysis"
    )

    assert (
        decision["arguments_json"]
        == tool_call.function.arguments
    )

    create_kwargs = (
        agent.client.chat.completions.kwargs
    )

    assert create_kwargs["tools"] == (
        agent.tool_schemas
    )


if __name__ == "__main__":

    test_decide_next_action_returns_tool_call()

    print(
        "LLM agent tool decision test passed."
    )