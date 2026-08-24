"""Offline V4 behavior evaluations using the real option LangGraph."""

from datetime import datetime, timedelta, timezone

from agent.result_formatter import ResultFormatter
from core.exceptions import (
    ExpirationNotFoundError,
    MarketDataUnavailableError,
)
from graph.option_graph import build_option_graph
from schemas.analysis_request import AnalysisRequest
from schemas.analysis_result import AnalysisResult
from schemas.data_quality_report import DataQualityReport
from tools.natural_date_resolver import NaturalDateResolver


TOOL_ARGUMENTS = (
    '{"ticker":"TSLA","expiration":"2026-08-28",'
    '"analysis_types":["gex"]}'
)


class BaseFakeAgent:

    def __init__(self):
        self.decision_inputs = []
        self.execution_count = 0

    def execute_tool_call(
        self,
        tool_name,
        arguments_json,
        trace_id=None,
    ):
        self.execution_count += 1

        return {
            "request": AnalysisRequest(
                ticker="TSLA",
                expiration="2026-08-28",
                analysis_types=["gex"],
            ),
            "analysis_result": AnalysisResult(
                ticker="TSLA",
                expiration="2026-08-28",
            ),
            "analysis_context": "Ticker: TSLA\nTotal GEX: 100.0",
        }

    @staticmethod
    def tool_decision():
        return {
            "decision_type": "tool_call",
            "tool_call_id": "call_eval",
            "tool_name": "run_option_analysis",
            "arguments_json": TOOL_ARGUMENTS,
        }


class ToolThenAnswerAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)

        if kwargs["tool_observations"]:
            return {
                "decision_type": "final_answer",
                "content": "Tool result is sufficient.",
            }

        return self.tool_decision()


class DirectAnswerAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)

        return {
            "decision_type": "final_answer",
            "content": "Explanation from fresh context.",
        }


class InvalidRequestAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)
        return self.tool_decision()

    def execute_tool_call(self, *args, **kwargs):
        raise ValueError("Missing tool arguments: ['ticker']")


class ExpirationFailureAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)
        return self.tool_decision()

    def execute_tool_call(self, *args, **kwargs):
        raise ExpirationNotFoundError(
            ticker="TSLA",
            requested_expiration="2035-01-01",
            available_expirations=["2026-08-28"],
        )


class UnavailableMarketAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)
        return self.tool_decision()

    def execute_tool_call(self, *args, **kwargs):
        self.execution_count += 1
        raise MarketDataUnavailableError(
            source="OptionCharts",
            operation="option_chain",
        )


class DuplicateToolAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)
        observations = kwargs["tool_observations"]

        if len(observations) >= 2:
            return {
                "decision_type": "final_answer",
                "content": "Duplicate call was blocked.",
            }

        return self.tool_decision()


class EndlessToolAgent(BaseFakeAgent):

    def decide_next_action(self, **kwargs):
        self.decision_inputs.append(kwargs)
        analysis_types = ["gex", "dex", "oi", "max_pain"]
        call_index = len(self.decision_inputs) - 1

        return {
            "decision_type": "tool_call",
            "tool_call_id": f"call_endless_{call_index}",
            "tool_name": "run_option_analysis",
            "arguments_json": (
                '{"ticker":"TSLA","expiration":"2026-08-28",'
                f'"analysis_types":["{analysis_types[call_index % 4]}"]}}'
            ),
        }


def invoke_graph(agent, state):
    """Run a complete graph invocation without model or market dependencies."""

    return build_option_graph(agent).invoke(state)


def test_new_analysis_uses_one_tool_then_answers():

    agent = ToolThenAnswerAgent()

    result = invoke_graph(
        agent,
        {"user_input": "Analyze TSLA GEX for 2026-08-28"},
    )

    assert agent.execution_count == 1
    assert len(agent.decision_inputs) == 2
    assert result["final_answer"] == "Tool result is sufficient."
    assert result["tool_observations"][0]["status"] == "success"


def test_fresh_context_allows_direct_explanation():

    agent = DirectAnswerAgent()

    result = invoke_graph(
        agent,
        {
            "user_input": "Explain that further.",
            "analysis_context": "Fresh option data",
            "last_successful_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
    )

    assert agent.execution_count == 0
    assert agent.decision_inputs[0]["has_fresh_analysis"] is True
    assert result["final_answer"] == "Explanation from fresh context."


def test_stale_context_requires_new_tool_result():

    agent = ToolThenAnswerAgent()

    result = invoke_graph(
        agent,
        {
            "user_input": "Analyze TSLA GEX again.",
            "analysis_context": "Stale option data",
            "last_successful_at": (
                datetime.now(timezone.utc)
                - timedelta(minutes=6)
            ).isoformat(),
        },
    )

    assert agent.decision_inputs[0]["has_fresh_analysis"] is False
    assert agent.execution_count == 1
    assert result["final_answer"] == "Tool result is sufficient."


def test_invalid_tool_arguments_return_controlled_answer():

    result = invoke_graph(
        InvalidRequestAgent(),
        {"user_input": "Analyze TSLA GEX."},
    )

    assert result["final_answer"].startswith("请求参数无效：")


def test_missing_expiration_returns_available_alternative():

    result = invoke_graph(
        ExpirationFailureAgent(),
        {"user_input": "Analyze TSLA GEX."},
    )

    assert "未找到 TSLA 在 2035-01-01" in result["final_answer"]
    assert "2026-08-28" in result["final_answer"]


def test_market_data_failure_stops_after_two_attempts():

    agent = UnavailableMarketAgent()

    result = invoke_graph(
        agent,
        {"user_input": "Analyze TSLA GEX."},
    )

    assert agent.execution_count == 2
    assert result["loop_termination_reason"] == (
        "max_consecutive_tool_failures"
    )
    assert "数据源连续不可用" in result["final_answer"]


def test_duplicate_tool_call_is_blocked_without_second_execution():

    agent = DuplicateToolAgent()

    result = invoke_graph(
        agent,
        {"user_input": "Analyze TSLA GEX."},
    )

    assert agent.execution_count == 1
    assert result["tool_observations"][1]["status"] == "duplicate"
    assert result["final_answer"] == "Duplicate call was blocked."


def test_loop_max_steps_stops_endless_tool_calls():

    agent = EndlessToolAgent()

    result = invoke_graph(
        agent,
        {"user_input": "Analyze TSLA GEX."},
    )

    assert agent.execution_count == 3
    assert result["loop_termination_reason"] == "max_tool_steps"
    assert "安全步骤上限" in result["final_answer"]


def test_relative_date_resolution_is_deterministic():

    resolved = NaturalDateResolver().resolve(
        "Analyze TSLA next Friday GEX",
        datetime(2026, 8, 17).date(),
    )

    assert resolved == "2026-08-28"


def test_data_quality_warning_reaches_agent_context():

    context = ResultFormatter().format(
        AnalysisResult(
            ticker="TSLA",
            expiration="2026-08-28",
            data_quality_report=DataQualityReport(
                source="OptionCharts",
                fetched_at=datetime(
                    2026,
                    8,
                    24,
                    tzinfo=timezone.utc,
                ),
                cache_state="miss",
                contract_count=0,
                warnings=["The retrieved option chain contains no contracts."],
            ),
        )
    )

    assert "DATA QUALITY WARNING:" in context


if __name__ == "__main__":

    test_new_analysis_uses_one_tool_then_answers()
    test_fresh_context_allows_direct_explanation()
    test_stale_context_requires_new_tool_result()
    test_invalid_tool_arguments_return_controlled_answer()
    test_missing_expiration_returns_available_alternative()
    test_market_data_failure_stops_after_two_attempts()
    test_duplicate_tool_call_is_blocked_without_second_execution()
    test_loop_max_steps_stops_endless_tool_calls()
    test_relative_date_resolution_is_deterministic()
    test_data_quality_warning_reaches_agent_context()

    print("All V4 offline evaluation cases passed.")
