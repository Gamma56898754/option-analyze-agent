
from agent.llm_agent import LLMAgent


class FakeToolExecutor:

    def __init__(self):

        self.tool_name = None

        self.arguments_json = None

    def execute(
        self,
        tool_name,
        arguments_json,
    ):

        self.tool_name = tool_name

        self.arguments_json = arguments_json

        return {
            "analysis_context": "fake-tool-result"
        }


def test_llm_agent_execute_tool_call():

    agent = LLMAgent.__new__(
        LLMAgent
    )

    fake_executor = FakeToolExecutor()

    agent.tool_executor = fake_executor

    tool_name = "run_option_analysis"

    arguments_json = '{"ticker": "TSLA"}'

    result = agent.execute_tool_call(
        tool_name=tool_name,
        arguments_json=arguments_json,
    )

    assert result == {
        "analysis_context": "fake-tool-result"
    }

    assert fake_executor.tool_name == (
        "run_option_analysis"
    )

    assert fake_executor.arguments_json == (
        '{"ticker": "TSLA"}'
    )


if __name__ == "__main__":

    test_llm_agent_execute_tool_call()

    print(
        "LLM agent tool execution test passed."
    )