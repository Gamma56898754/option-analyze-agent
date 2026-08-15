from operator import add
from typing import Annotated, TypedDict

from schemas.analysis_request import AnalysisRequest
from schemas.analysis_result import AnalysisResult


class OptionAgentState(TypedDict, total=False):
    """
    Shared data for one option-analysis conversation.
    """

    user_input: str
    request: AnalysisRequest
    validation_error: str | None
    analysis_result: AnalysisResult
    analysis_context: str
    final_answer: str
    error: str | None
    analysis_error: str | None

    available_expirations: list[str]

    conversation_history: Annotated[
        list[dict[str, str]],
        add
    ]

    running_summary: str | None

    last_successful_request: dict[str, object] | None