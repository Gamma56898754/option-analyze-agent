import json

from agent.tool_schemas import (
    OPTION_ANALYSIS_TOOL,
    OPTION_ANALYSIS_TOOLS,
)


def test_option_analysis_tool_schema():

    assert len(OPTION_ANALYSIS_TOOLS) == 1

    assert OPTION_ANALYSIS_TOOLS[0] == OPTION_ANALYSIS_TOOL

    assert OPTION_ANALYSIS_TOOL["type"] == "function"

    function = OPTION_ANALYSIS_TOOL["function"]

    assert function["name"] == "run_option_analysis"

    parameters = function["parameters"]

    assert parameters["type"] == "object"

    assert set(parameters["required"]) == {
        "ticker",
        "expiration",
        "analysis_types",
    }

    properties = parameters["properties"]

    assert set(properties.keys()) == {
        "ticker",
        "expiration",
        "analysis_types",
        "force_refresh",
    }

    assert set(
        properties["analysis_types"]["items"]["enum"]
    ) == {
        "gex",
        "dex",
        "oi",
        "maxpain",
    }

    json.dumps(OPTION_ANALYSIS_TOOLS)


if __name__ == "__main__":

    test_option_analysis_tool_schema()

    print("Option analysis tool schema test passed.")