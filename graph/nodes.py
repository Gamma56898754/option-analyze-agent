from agent.llm_agent import LLMAgent
from graph.state import OptionAgentState
from langgraph.types import Overwrite
from tools.market_time_tool import MarketTimeTool
from tools.natural_date_resolver import NaturalDateResolver
from core.exceptions import ExpirationNotFoundError


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

        answer = self.agent.generate_analysis(
            user_input=state["user_input"],
            analysis_context=state["analysis_context"]
        )

        return {
            "final_answer": answer
        }

    def update_short_term_memory_node(
        self,
        state: OptionAgentState,
    ) -> dict:

        request = state["request"]

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

        if not state.get("analysis_error"):
            memory_update[
                "last_successful_request"
            ] = {
                "ticker": request.ticker,
                "expiration": request.expiration,
                "analysis_types": request.analysis_types,
            }

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
            []
        )

        recent_messages = history[-4:]
        messages_to_summarize = history[:-4]

        if not messages_to_summarize:
            return {}

        summary = self.agent.summarize_conversation(
            previous_summary=state.get(
                "running_summary"
            ),
            messages_to_summarize=messages_to_summarize,
        )

        return {
            "running_summary": summary,
            "conversation_history": Overwrite(
                recent_messages
            ),
        }