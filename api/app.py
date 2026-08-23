import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
import asyncio
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from memory.conversation_store import (
    ConversationStore,
)

import time
from uuid import uuid4
from core.trace import log_trace_event

from core.exceptions import (
    MarketDataUnavailableError,
)

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from agent.llm_agent import LLMAgent
from api.api_contracts import (
    ChatRequest,
    ChatResponse,
    ConversationMessageResponse,
    ConversationResponse,
    ConversationTitleUpdate,
    HealthResponse,
)
from core.checkpoint_factory import (
    create_sqlite_checkpointer,
)
from core.runtime import Runtime
from graph.option_graph import build_option_graph

logger = logging.getLogger(
    __name__
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WEB_DIR = PROJECT_ROOT / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):

    load_dotenv()

    api_key = os.getenv(
        "DEEPSEEK_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "DEEPSEEK_API_KEY not found. "
            "Please check your .env file."
        )

    runtime = await asyncio.to_thread(
        Runtime
    )

    agent = LLMAgent(
        runtime=runtime,
        api_key=api_key,
    )

    checkpointer, db_connection = (
        create_sqlite_checkpointer(
            PROJECT_ROOT
            / "memory"
            / "option_agent_checkpoints.db"
        )
    )

    conversation_store = ConversationStore(
        PROJECT_ROOT
        / "memory"
        / "conversations.db"
    )

    graph = build_option_graph(
        agent,
        checkpointer=checkpointer,
    )

    app.state.graph = graph
    app.state.graph_lock = Lock()
    app.state.conversation_store = (conversation_store)
    app.state.db_connection = db_connection

    yield

    db_connection.close()


app = FastAPI(
    title="Option Analyze Agent API",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=WEB_DIR),
    name="static",
)


@app.get(
    "/",
    include_in_schema=False,
)
def serve_chat_page():
    return FileResponse(
        WEB_DIR / "index.html"
    )

@app.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:

    return HealthResponse(
        status="ok"
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
)


def chat(
    chat_request: ChatRequest,
    request: Request,
) -> ChatResponse:

    user_input = chat_request.message.strip()

    if not user_input:
        raise HTTPException(
            status_code=422,
            detail="message must not be blank",
        )

    trace_id = uuid4().hex

    thread_id = (
        chat_request.thread_id
        or f"api-{uuid4().hex}"
    )

    started_at = time.perf_counter()

    log_trace_event(
        trace_id=trace_id,
        event="chat_started",
        thread_id=thread_id,
        message_length=len(user_input),
    )
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    try:

        with request.app.state.graph_lock:

            result = request.app.state.graph.invoke(
                {
                    "trace_id": trace_id,
                    "user_input": user_input,
                },
                config=config,
            )

    except MarketDataUnavailableError as exc:

        logger.warning(
            "Market data unavailable. "
            "thread_id=%s source=%s operation=%s "
            "status_code=%s",
            thread_id,
            exc.source,
            exc.operation,
            exc.status_code,
        )

        log_trace_event(
            trace_id=trace_id,
            event="chat_data_source_unavailable",
            thread_id=thread_id,
            source=exc.source,
            operation=exc.operation,
            status_code=exc.status_code,
            duration_ms=round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            ),
        )

        answer = (
            "期权行情数据源暂时不可用，"
            "本次未生成新的期权分析。"
            "请稍后重试 最好将你的IP ADDRESS切换为美利坚地区。"
        )

        request.app.state.conversation_store.save_turn(
            thread_id=thread_id,
            user_message=user_input,
            assistant_message=answer,
        )

        return ChatResponse(
            thread_id=thread_id,
            answer=answer,
            decision_type="final_answer",
            trace_id=trace_id,
        )

    except Exception as exc:

        logger.exception(
            "Agent execution failed. thread_id=%s",
            thread_id,
        )

        log_trace_event(
            trace_id=trace_id,
            event="chat_failed",
            thread_id=thread_id,
            duration_ms=round(
                (
                    time.perf_counter()
                    - started_at
                ) * 1000,
                2,
            ),
            error_type=type(exc).__name__,
        )

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed.",
        ) from exc

    decision = result.get(
        "agent_decision",
        {},
    )

    decision_type = decision.get(
        "decision_type"
    )

    if decision_type not in {
        "tool_call",
        "final_answer",
    }:
        raise HTTPException(
            status_code=500,
            detail="Unknown agent decision type.",
        )

    answer = result.get("final_answer")

    if not answer:
        raise HTTPException(
            status_code=500,
            detail="Agent returned no final answer.",
        )

    request.app.state.conversation_store.save_turn(
        thread_id=thread_id,
        user_message=user_input,
        assistant_message=answer,
    )

    log_trace_event(
        trace_id=trace_id,
        event="chat_completed",
        thread_id=thread_id,
        decision_type=decision_type,
        duration_ms=round(
            (
                time.perf_counter()
                - started_at
            ) * 1000,
            2,
        ),
    )

    return ChatResponse(
        thread_id=thread_id,
        answer=answer,
        decision_type=decision_type,
        trace_id=trace_id,
    )

@app.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
def list_conversations(
    request: Request,
):

    return request.app.state.conversation_store.list_recent()


@app.get(
    "/conversations/{thread_id}/messages",
    response_model=list[
        ConversationMessageResponse
    ],
)
def get_conversation_messages(
    thread_id: str,
    request: Request,
):

    return (
        request.app.state
        .conversation_store
        .get_messages(thread_id)
    )


@app.patch(
    "/conversations/{thread_id}",
    response_model=ConversationResponse,
)
def update_conversation_title(
    thread_id: str,
    title_update: ConversationTitleUpdate,
    request: Request,
):

    updated = (
        request.app.state
        .conversation_store
        .update_title(
            thread_id=thread_id,
            title=title_update.title,
        )
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    conversations = (
        request.app.state
        .conversation_store
        .list_recent()
    )

    for conversation in conversations:

        if conversation["thread_id"] == thread_id:
            return conversation

    raise HTTPException(
        status_code=500,
        detail=(
            "Conversation was updated "
            "but could not be loaded."
        ),
    )
