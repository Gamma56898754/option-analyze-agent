from typing import Literal
from typing import Literal
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):

    status: Literal["ok"]


class ChatRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=4000,
        description="User message for the option agent.",
    )

    thread_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description=(
            "Optional conversation identifier. "
            "The server creates one when omitted."
        ),
    )


class ChatResponse(BaseModel):

    thread_id: str

    thread_id: str

    answer: str

    decision_type: Literal[
        "tool_call",
        "final_answer",
    ]

class ConversationResponse(BaseModel):

    thread_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessageResponse(
    BaseModel
):

    id: int
    thread_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class ConversationTitleUpdate(
    BaseModel
):

    title: str = Field(
        min_length=1,
        max_length=100,
        description=(
            "User-visible conversation title."
        ),
    )