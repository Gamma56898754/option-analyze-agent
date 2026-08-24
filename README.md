# Option Analyze Agent

Option Analyze Agent is a local, single-user AI application for US equity
option-chain analysis. It retrieves data from OptionCharts, calculates market
metrics with deterministic Python code, and uses an LLM for controlled tool
selection and natural-language explanation.

> For learning and research only. This project is not investment advice.
> External market data can be delayed, incomplete, unavailable, or changed.

## Core engineering components

| Area | What the application implements |
| --- | --- |
| Market-data pipeline | OptionCharts retrieval, expiration discovery, HTML parsing, normalized option-contract schemas, and typed failure handling. |
| Deterministic analytics | GEX, DEX, OI, and Max Pain calculations in separate Python modules with structured results. |
| AI orchestration | Native Tool Calling, LangGraph state and routing, natural-date resolution, session context, short-term memory, and summary memory. |
| Backend and user access | FastAPI chat API, browser chat page, PyWebView desktop launcher, CLI, API contracts, and session identifiers. |
| Storage and performance | SQLite checkpoints and conversation history, plus an in-memory five-minute option-chain cache. |
| Reliability and diagnosis | Domain exceptions, controlled user-facing errors, JSONL traces, data-quality provenance, and offline regression tests. |
| Extensibility | A reusable option Skill and an MCP adapter that exposes existing business logic without duplicating calculations. |

## Version progression

| Version | Main result |
| --- | --- |
| V1 | End-to-end option-chain retrieval, parsing, deterministic metrics, and LLM explanation. |
| V2 | LangGraph state, conditional routing, persistent memory, caching, and natural-language dates. |
| V3 | Native Tool Calling, FastAPI, browser and desktop interfaces, traces, and persisted sessions. |
| V4 | Option Skill, bounded Agent Loop, data quality and provenance, local MCP Server, and an offline evaluation suite. |

## V4 highlights

- Uses native LLM Tool Calling through one controlled public tool:
  run_option_analysis.
- Validates tool names, JSON arguments, tickers, expirations, analysis types,
  and unexpected arguments before business logic is run.
- Implements a bounded Agent Loop: after a tool observation, the Agent decides
  whether to answer or make a distinct follow-up tool call.
- Prevents runaway loops with a three-tool-step limit, duplicate-call
  protection, a consecutive market-data-failure limit, and a LangGraph
  recursion limit.
- Loads an option-analysis Skill containing intents, freshness rules,
  constraints, and answer requirements.
- Keeps successful analysis context fresh for five minutes, so
  explanation-only follow-ups can avoid unnecessary market-data calls.
- Produces a DataQualityReport with source, fetch time, cache state, contract
  count, and material warnings.
- Provides a local stdio MCP Server and offline evaluation tests.

## Architecture

    Web UI / Desktop App / CLI
                |
                v
         FastAPI POST /chat
                |
                | thread_id + trace_id
                v
         LangGraph StateGraph
                |
                +--> initialize_agent_loop
                |
                +--> agent_decide_node
                |       |
                |       +--> direct_answer_node
                |       |
                |       +--> execute_tool_call_node
                |                 |
                |                 v
                |           OptionToolExecutor
                |                 |
                |                 v
                |           AnalysisRunner
                |                 |
                |                 +--> OptionChainCache
                |                 +--> OptionCharts Client -> HTML Parser
                |                 +--> GEX / DEX / OI / Max Pain Tools
                |                 |
                |                 v
                |           tool observation
                |                 |
                |                 +--> agent_decide_node
                |
                +--> update_short_term_memory_node
                +--> summarize_conversation_node (when needed)
                |
                v
    ChatResponse + SQLite conversation history + JSONL trace

    MCP-compatible Host
                |
                v
       Local stdio MCP Server
                |
                v
      OptionToolExecutor (same business logic)

The LLM is responsible for intent understanding, controlled tool selection, and
explanation. Retrieval, validation, caching, calculations, persistence, and
loop safety are handled by deterministic application code.

## Project layout

    agent/       LLM integration, tool schemas, execution, result formatting
    analysis/    Deterministic GEX, DEX, OI, and Max Pain calculations
    api/         FastAPI application and API contracts
    cache/       In-memory option-chain cache
    core/        Runtime, runner, validation, exceptions, checkpoints, tracing
    data/        OptionCharts client and HTML parser
    graph/       LangGraph state, nodes, routing, and graph assembly
    mcp_server/  Local stdio MCP adapter
    memory/      Local SQLite databases created at runtime
    schemas/     Shared data structures and result schemas
    skills/      LLM skill instructions
    tools/       Market-data, date-resolution, and metric tools
    web/         Browser chat UI assets
    test/        Offline unit, integration, regression, and evaluation tests

## Request flow

1. A user sends text and a thread_id through the UI, CLI, or API.
2. FastAPI creates a trace_id and invokes LangGraph with SQLite checkpointing.
3. The graph initializes the per-turn loop, loads context, resolves natural
   dates, and checks whether prior analysis is still fresh.
4. The Agent chooses a direct answer or run_option_analysis.
5. OptionToolExecutor validates LLM JSON and creates an AnalysisRequest.
6. AnalysisRunner checks the cache. On a miss or explicit refresh, it retrieves
   and parses source data, then runs selected deterministic metrics.
7. The formatted analysis and data-quality information return as a tool
   observation. The Agent decides whether more distinct data is needed or
   produces an answer.
8. The graph updates memory and summarizes older messages when appropriate.
   FastAPI persists display history and returns the response.

## Requirements and installation

- Python 3.12+
- A DeepSeek API key compatible with the OpenAI Python SDK interface
- Playwright Chromium for live OptionCharts retrieval

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    playwright install chromium

Create a .env file in the project root:

    DEEPSEEK_API_KEY=your_api_key_here

Do not commit .env, virtual environments, logs, or local SQLite databases.

## Run

### Desktop app

    python -m desktop_app

### Browser and API mode

    uvicorn api.app:app

Open http://127.0.0.1:8000/. API documentation is at
http://127.0.0.1:8000/docs.

### CLI

    python -m run_graph_agent

Use exit, quit, or 退出 to stop the CLI.

### Local MCP Server

    python -m mcp_server.option_server

The MCP Server is a stdio process for MCP-compatible hosts, not an interactive
terminal program. See [docs/MCP_SERVER.md](docs/MCP_SERVER.md) for its contract
and Cursor configuration.

## Example requests

    Analyze TSLA GEX and DEX for 2026-08-28
    Analyze Tesla for next Friday
    Explain the previous GEX result in more detail
    Refresh the data and analyze it again

## Data freshness, quality, and observability

- Option-chain cache TTL: five minutes, keyed by ticker + expiration.
- Cache hit reuses parsed data; a cache miss retrieves it; explicit refresh
  bypasses the cache.
- Analysis context older than five minutes is not presented as current market
  data to the Agent.
- Quality output contains source, fetch timestamp, cache state, contract count,
  and warnings.
- Checkpoints: memory/option_agent_checkpoints.db
- Browser history: memory/conversations.db
- Request trace: logs/option_agent.jsonl

Common trace events include chat_started, agent_decision_completed,
tool_execution_completed, option_chain_cache_hit,
option_chain_fetch_completed, analysis_calculation_completed, and
agent_loop_terminated.

## Tests

    python -m test.test_evaluation_suite
    python -m test.test_mcp_option_service
    pytest test/test_mcp_server_integration.py

See [docs/EVALUATION.md](docs/EVALUATION.md) for V4 acceptance criteria.

## Current boundaries

- This is a local, single-user application. Its in-memory cache, SQLite
  storage, JSONL tracing, and serialized graph execution are not multi-user
  production infrastructure.
- OptionCharts is an external dependency and may be unavailable, rate-limited,
  verification-protected, or structurally changed.
- The Agent Loop supports multiple controlled attempts, but the model currently
  has one public aggregate business tool: run_option_analysis.
- Authentication, tenant isolation, Redis, PostgreSQL, centralized monitoring,
  CI/CD, cloud deployment, RAG, and multi-agent architecture are not included.

For multi-user production deployment, add authentication, an approved data
source, PostgreSQL, Redis, centralized observability, CI, and containers.

---

# 中文说明

## 项目简介

Option Analyze Agent 是一个本地、单用户的美股期权链分析 AI 应用。它从
OptionCharts 获取期权链数据，使用确定性 Python 代码计算 GEX、DEX、持仓量
（OI）与 Max Pain，再由 LLM 在受控范围内决定是否需要取数并解释结果。

> 本项目仅供学习与研究使用，不构成投资建议。市场数据可能延迟、不完整、
> 不可用，或因数据源结构变化而失效。

## 主要工程内容

| 模块 | 当前实现内容 |
| --- | --- |
| 市场数据链路 | OptionCharts 获取、可用到期日发现、HTML 解析、统一期权合约结构和类型化异常。 |
| 确定性分析 | GEX、DEX、OI、Max Pain 分别由 Python 模块计算，并输出结构化结果。 |
| AI 编排 | Tool Calling、LangGraph 状态和路由、自然语言日期、会话上下文、短期记忆和摘要记忆。 |
| 后端与用户入口 | FastAPI 聊天 API、浏览器聊天页面、PyWebView 桌面启动器、CLI、API 合同和会话标识。 |
| 存储与性能 | SQLite 检查点和会话历史，以及五分钟内存期权链缓存。 |
| 可靠性与诊断 | 领域异常、受控用户错误、JSONL Trace、数据质量溯源和离线回归测试。 |
| 可扩展性 | 可复用的 Option Skill，以及不重复业务计算的 MCP 适配层。 |

## 版本演进

| 版本 | 主要成果 |
| --- | --- |
| V1 | 期权链抓取、解析、确定性指标计算和 LLM 分析闭环。 |
| V2 | LangGraph 状态、条件路由、持久化记忆、缓存和自然语言日期。 |
| V3 | 原生 Tool Calling、FastAPI、网页与桌面端、Trace 和会话持久化。 |
| V4 | Option Skill、有边界的 Agent Loop、数据质量与溯源、本地 MCP Server 和离线评估套件。 |

## 当前 V4 功能

- 通过原生 Tool Calling 调用受控的 run_option_analysis 工具。
- 校验工具名、JSON 参数、Ticker、到期日、指标类型和多余字段。
- 支持 Agent Loop：工具结果回到 Agent 后，Agent 判断直接回答或继续不同调用。
- 通过最大工具步骤、重复调用拦截、连续数据源失败上限和图递归上限避免失控。
- 通过 Option Analysis Skill 提供支持意图、数据新鲜度和回答约束。
- 成功分析后的上下文在五分钟内可用于追问解释，避免不必要取数。
- 输出数据来源、抓取时间、缓存状态、合约数量和数据质量警告。
- 提供本地 stdio MCP Server 和离线评估测试。

## 快速启动

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    playwright install chromium

在根目录创建 .env：

    DEEPSEEK_API_KEY=your_api_key_here

启动桌面端：

    python -m desktop_app

启动浏览器/API 开发模式：

    uvicorn api.app:app

启动 MCP Server：

    python -m mcp_server.option_server

MCP Server 面向 Cursor 等 MCP Host，不是交互式终端程序。详细配置请见
[docs/MCP_SERVER.md](docs/MCP_SERVER.md)。

## 常用测试

    python -m test.test_evaluation_suite
    python -m test.test_mcp_option_service
    pytest test/test_mcp_server_integration.py

## 当前边界

该项目适合本地单用户学习和演示，尚未具备多人生产部署所需的认证、多租户、
PostgreSQL、Redis、集中监控、CI/CD、容器化部署、RAG 和多 Agent 架构。

