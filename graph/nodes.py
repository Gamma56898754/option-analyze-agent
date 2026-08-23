from agent.llm_agent import LLMAgent
from graph.state import OptionAgentState
from langgraph.types import Overwrite
from tools.market_time_tool import MarketTimeTool
from tools.natural_date_resolver import NaturalDateResolver
from core.exceptions import ExpirationNotFoundError
from schemas.analysis_request import AnalysisRequest
import json
import time
from datetime import datetime, timedelta, timezone

from cache.option_chain_cache import CACHE_TTL_SECONDS
from core.trace import log_trace_event


class OptionGraphNodes:
    """
    Nodes used by the option-analysis LangGraph.
    """

    def __init__(self, agent: LLMAgent):
        self.agent = agent
        self.market_time_tool = MarketTimeTool()

        self.natural_date_resolver = (
            NaturalDateResolver()
        )

    @staticmethod
    def _trace(
        state: OptionAgentState,
        event: str,
        **fields,
    ) -> None:
        """Write a node-level event when this run has a trace ID."""

        trace_id = state.get("trace_id")

        if trace_id is None:
            return

        log_trace_event(
            trace_id=trace_id,
            event=event,
            **fields,
        )

    def _has_fresh_analysis_context(
        self,
        state: OptionAgentState,
        ) -> bool:

        completed_at_text = state.get(
            "last_successful_at"
        )

        if (
            not completed_at_text
            or not state.get("analysis_context")
        ):
            return False

        try:

            completed_at = datetime.fromisoformat(
                completed_at_text.replace(
                    "Z",
                    "+00:00",
                )
            )

        except ValueError:
            return False

        if completed_at.tzinfo is None:
            completed_at = completed_at.replace(
                tzinfo=timezone.utc
            )

        age = datetime.now(
            timezone.utc
        ) - completed_at

        return (
            timedelta(seconds=0)
            <= age
            <= timedelta(
                seconds=CACHE_TTL_SECONDS
            )
        )

    def agent_decide_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        started_at = time.perf_counter()

        self._trace(
            state,
            "agent_decision_started",
        )

        market_context = (
            self.market_time_tool
            .get_market_context()
        )

        resolved_expiration = (
            self.natural_date_resolver
            .resolve(
                user_input=state["user_input"],
                market_date=(
                    market_context.current_time
                    .date()
                ),
            )
        )

        has_fresh_analysis = (
            self._has_fresh_analysis_context(
                state
            )
        )

        if (
            state.get("analysis_context")
            and not has_fresh_analysis
        ):
            print(
                "Existing analysis context expired; "
                "new market data is required."
            )

        try:
            decision = self.agent.decide_next_action(
                user_input=state["user_input"],
                conversation_history=(
                    state.get(
                        "conversation_history",
                        [],
                    )
                    if has_fresh_analysis
                    else []
                ),
                last_successful_request=state.get(
                    "last_successful_request"
                ),
                running_summary=(
                    state.get("running_summary")
                    if has_fresh_analysis
                    else None
                ),
                market_date=(
                    market_context.current_time
                    .date()
                    .isoformat()
                ),
                resolved_expiration=resolved_expiration,
                analysis_context=(
                    state.get("analysis_context")
                    if has_fresh_analysis
                    else None
                ),
                has_fresh_analysis=has_fresh_analysis,
            )
        except Exception as exc:
            self._trace(
                state,
                "agent_decision_failed",
                duration_ms=round(
                    (time.perf_counter() - started_at) * 1000,
                    2,
                ),
                error_type=type(exc).__name__,
            )
            raise

        if (
            decision["decision_type"]
            == "tool_call"
            and resolved_expiration is not None
        ):

            try:

                arguments = json.loads(
                    decision["arguments_json"]
                )

            except json.JSONDecodeError:

                # Executor will later return
                # a controlled validation error.
                pass

            else:

                arguments["expiration"] = (
                    resolved_expiration
                )

                decision["arguments_json"] = (
                    json.dumps(arguments)
                )

                print(
                    "Natural date resolved:",
                    resolved_expiration,
                )

        self._trace(
            state,
            "agent_decision_completed",
            decision_type=decision["decision_type"],
            tool_name=decision.get("tool_name"),
            has_fresh_analysis=has_fresh_analysis,
            has_resolved_expiration=(
                resolved_expiration is not None
            ),
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
        )

        return {
            "agent_decision": decision
        }

    def execute_tool_call_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        decision = state["agent_decision"]

        if (
            decision["decision_type"]
            != "tool_call"
        ):

            raise ValueError(
                "Expected a tool_call decision"
            )

        started_at = time.perf_counter()

        self._trace(
            state,
            "tool_execution_started",
            tool_name=decision["tool_name"],
        )

        try:

            execution_result = (
                self.agent.execute_tool_call(
                    tool_name=decision[
                        "tool_name"
                    ],
                    arguments_json=decision[
                        "arguments_json"
                    ],
                    trace_id=state.get(
                        "trace_id"
                    ),
                )
            )

        except ExpirationNotFoundError as exc:

            self._trace(
                state,
                "tool_execution_failed",
                tool_name=decision["tool_name"],
                error_type=type(exc).__name__,
                reason="expiration_not_found",
                duration_ms=round(
                    (time.perf_counter() - started_at) * 1000,
                    2,
                ),
            )

            return {
                "request": AnalysisRequest(
                    ticker=exc.ticker,
                    expiration=(
                        exc.requested_expiration
                    ),
                    analysis_types=[],
                ),
                "analysis_error": (
                    "expiration_not_found"
                ),
                "available_expirations": (
                    exc.available_expirations
                ),
            }

        except ValueError as exc:

            self._trace(
                state,
                "tool_execution_failed",
                tool_name=decision["tool_name"],
                error_type=type(exc).__name__,
                reason="validation_error",
                duration_ms=round(
                    (time.perf_counter() - started_at) * 1000,
                    2,
                ),
            )

            return {
                "validation_error": str(exc)
            }

        except Exception as exc:

            self._trace(
                state,
                "tool_execution_failed",
                tool_name=decision["tool_name"],
                error_type=type(exc).__name__,
                reason="unexpected_error",
                duration_ms=round(
                    (time.perf_counter() - started_at) * 1000,
                    2,
                ),
            )
            raise

        request = execution_result["request"]

        self._trace(
            state,
            "tool_execution_completed",
            tool_name=decision["tool_name"],
            ticker=request.ticker,
            expiration=request.expiration,
            analysis_types=request.analysis_types,
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
        )

        return {
            **execution_result,
            "validation_error": None,
            "analysis_error": None,
            "available_expirations": [],
            "last_successful_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def direct_answer_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        decision = state["agent_decision"]

        if (
            decision["decision_type"]
            != "final_answer"
        ):

            raise ValueError(
                "Expected a final_answer decision"
            )

        self._trace(
            state,
            "direct_answer_selected",
        )

        return {
            "final_answer": decision["content"]
        }

    def parse_request_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        market_context = (
            self.market_time_tool
            .get_market_context()
        )

        resolved_expiration = (
            self.natural_date_resolver
            .resolve(
                user_input=state["user_input"],
                market_date=(
                    market_context.current_time
                    .date()
                ),
            )
        )

        request = self.agent.create_request(
            user_input=state["user_input"],
            conversation_history=state.get(
                "conversation_history",
                []
            ),
            last_successful_request=state.get(
                "last_successful_request"
            ),
            running_summary=state.get(
                "running_summary"
            ),
            market_date=(
                market_context.current_time
                .date()
                .isoformat()
            )
        )

        if resolved_expiration is not None:
            print(
                "Natural date resolved:",
                resolved_expiration,
            )

            request.expiration = resolved_expiration

        return {
            "request": request
        }

    def validate_request_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        try:
            self.agent.validator.validate(
                state["request"]
            )
        except ValueError as exc:
            return {
                "validation_error": str(exc)
            }

        return {
            "validation_error": None
        }

    def validation_failed_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        return {
            "final_answer": (
                "请求参数无效："
                f"{state['validation_error']}"
            )
        }

    def run_analysis_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        try:
            analysis_result = self.agent.runner.run(
                state["request"]
            )

        except ExpirationNotFoundError as exc:
            return {
                "analysis_error": (
                    "expiration_not_found"
                ),
                "available_expirations": (
                    exc.available_expirations
                ),
            }

        return {
            "analysis_result": analysis_result,
            "analysis_error": None,
            "available_expirations": [],
        }

    def analysis_failed_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        request = state["request"]

        available_expirations = sorted(
            state.get(
                "available_expirations",
                [],
            )
        )

        suggested_expirations = [
            expiration
            for expiration in available_expirations
            if expiration >= request.expiration
        ][:3]

        if not suggested_expirations:
            suggested_expirations = (
                available_expirations[:3]
            )

        suggestions_text = "、".join(
            suggested_expirations
        )

        answer = (
            f"未找到 {request.ticker} 在 "
            f"{request.expiration} 到期的可用期权链数据。"
        )

        if suggestions_text:
            answer += (
                "\n\n可尝试的相邻可用到期日："
                f"{suggestions_text}。"
            )

        answer += (
            "\n\n请改用其中一个日期，或使用 "
            "“本周五 / 下周五”这类日期表达后再次提问。"
        )

        return {
            "final_answer": answer
        }

    def format_result_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        analysis_context = self.agent.formatter.format(
            state["analysis_result"]
        )

        return {
            "analysis_context": analysis_context
        }

    def generate_answer_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        started_at = time.perf_counter()

        self._trace(
            state,
            "answer_generation_started",
        )

        try:
            answer = self.agent.generate_answer_after_tool_call(
                user_input=state["user_input"],
                decision=state["agent_decision"],
                analysis_context=state["analysis_context"],
            )
        except Exception as exc:
            self._trace(
                state,
                "answer_generation_failed",
                duration_ms=round(
                    (time.perf_counter() - started_at) * 1000,
                    2,
                ),
                error_type=type(exc).__name__,
            )
            raise

        self._trace(
            state,
            "answer_generation_completed",
            answer_length=len(answer),
            duration_ms=round(
                (time.perf_counter() - started_at) * 1000,
                2,
            ),
        )

        return {
            "final_answer": answer,
        }

    def update_short_term_memory_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        started_at = time.perf_counter()

        request = state.get("request")

        memory_update = {
            "conversation_history": [
                {
                    "role": "user",
                    "content": state["user_input"],
                },
                {
                    "role": "assistant",
                    "content": state["final_answer"],
                },
            ],
        }

        saved_successful_request = False

        if (
            request is not None
            and state.get(
                "agent_decision",
                {},
            ).get("decision_type") == "tool_call"
            and not state.get("analysis_error")
            and not state.get("validation_error")
        ):
            memory_update[
                "last_successful_request"
            ] = {
                "ticker": request.ticker,
                "expiration": request.expiration,
                "analysis_types": request.analysis_types,
            }

            saved_successful_request = True

        self._trace(
            state,
            "short_term_memory_updated",
            added_message_count=2,
            saved_successful_request=(
                saved_successful_request
            ),
            duration_ms=round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            ),
        )

        return memory_update

    def summarize_conversation_node(
        self,
        state: OptionAgentState,
    ) -> dict:
        """
        Summarize older history and retain only recent raw messages.
        """

        history = state.get(
            "conversation_history",
            [],
        )

        recent_messages = history[-4:]
        messages_to_summarize = history[:-4]

        if not messages_to_summarize:

            self._trace(
                state,
                "conversation_summary_skipped",
                reason="no_old_messages",
            )

            return {}

        started_at = time.perf_counter()

        self._trace(
            state,
            "conversation_summary_started",
            summarized_message_count=len(
                messages_to_summarize
            ),
            retained_message_count=len(
                recent_messages
            ),
        )

        try:
            summary = self.agent.summarize_conversation(
                previous_summary=state.get(
                    "running_summary"
                ),
                messages_to_summarize=(
                    messages_to_summarize
                ),
            )

        except Exception as exc:

            self._trace(
                state,
                "conversation_summary_failed",
                error_type=type(exc).__name__,
                duration_ms=round(
                    (
                        time.perf_counter()
                        - started_at
                    ) * 1000,
                    2,
                ),
            )
            raise

        self._trace(
            state,
            "conversation_summary_completed",
            summarized_message_count=len(
                messages_to_summarize
            ),
            retained_message_count=len(
                recent_messages
            ),
            summary_length=len(summary),
            duration_ms=round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            ),
        )

        return {
            "running_summary": summary,
            "conversation_history": Overwrite(
                recent_messages
            ),
        }