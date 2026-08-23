import json

from agent.tool_calling.tool_executor import OptionToolExecutor


class FakeValidator:

    def __init__(self):

        self.request = None

    def validate(self, request):

        self.request = request

        return True


class FakeRunner:

    def __init__(self):

        self.request = None

    def run(self, request):

        self.request = request

        return "fake-analysis-result"


class FakeFormatter:

    def __init__(self):

        self.result = None

    def format(self, result):

        self.result = result

        return "formatted-analysis-context"


def test_execute_option_analysis_tool():

    validator = FakeValidator()

    runner = FakeRunner()

    formatter = FakeFormatter()

    executor = OptionToolExecutor(
        runner=runner,
        validator=validator,
        formatter=formatter,
    )

    execution_result = executor.execute(
        tool_name="run_option_analysis",
        arguments_json=json.dumps(
            {
                "ticker": "tsla",
                "expiration": "2026-08-21",
                "analysis_types": [
                    "gex",
                    "dex",
                ],
            }
        ),
    )

    assert execution_result[
        "analysis_context"
    ] == "formatted-analysis-context"

    assert execution_result[
        "analysis_result"
    ] == "fake-analysis-result"

    assert validator.request is not None

    assert execution_result["request"] is not None

    assert execution_result["request"].ticker == "TSLA"

    assert execution_result["request"].expiration == (
        "2026-08-21"
    )

    assert execution_result["request"].analysis_types == [
        "gex",
        "dex",
    ]

    assert execution_result["request"].force_refresh is False

    assert formatter.result == (
        "fake-analysis-result"
    )


if __name__ == "__main__":

    test_execute_option_analysis_tool()

    print("Option tool executor test passed.")