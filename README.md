# Option Analyze Agent

An LLM-powered options analysis agent that retrieves option-chain data, runs deterministic GEX / DEX / OI / Max Pain calculations, and explains the results in natural language.

The project is currently at the **LangGraph V2** milestone: it supports a stateful CLI conversation, persistent checkpoints, short-term memory summarization, option-chain caching, natural-language date handling, and controlled error routing.

> Educational and research use only. This project is not financial advice.

## Features

- Fetches option-chain and expiration data from OptionCharts.
- Reuses a Playwright-created browser session and a `requests.Session` client during one application run.
- Runs deterministic analyses for:
  - Gamma Exposure (GEX)
  - Delta Exposure (DEX)
  - Open Interest (OI)
  - Max Pain
- Uses an LLM to convert natural-language requests into a validated `AnalysisRequest` and to explain calculated results.
- Supports a LangGraph workflow with validation, conditional routing, error handling, memory updates, and summarization.
- Persists LangGraph checkpoints in SQLite so the conversation can resume after restarting the CLI.
- Keeps recent raw conversation turns plus a compressed running summary.
- Reuses parsed `OptionChainResult` data for five minutes per `ticker + expiration` key.
- Supports explicit refresh requests that bypass the option-chain cache.
- Recognizes selected date expressions using the New York market date:
  - `today` / `今天`
  - `tomorrow` / `明天`
  - `this Friday` / `本周五`
  - `next Friday` / `下周五`
- Converts unavailable expirations into a user-facing response with real alternative expiration dates from the data source.



## Architecture

```text
User input
  -> parse_request
  -> validate_request
  -> conditional routing
       -> run_analysis
            -> format_result
            -> generate_answer
       -> generate_answer (explain an existing result)
       -> validation_failed
  -> update_short_term_memory
  -> summarize_conversation (when needed)
```

`run_analysis` has its own controlled branch:

```text
run_analysis
  -> success -> format_result -> generate_answer
  -> expiration unavailable -> analysis_failed -> user guidance
```



### Main modules

```text
agent/      LLM request parsing, result explanation, formatting
analysis/   Deterministic GEX, DEX, OI, and Max Pain calculations
cache/      In-memory OptionChainResult cache with a 5-minute TTL
core/       Runtime, validation, runner, and domain exceptions
data/       Browser bootstrap, OptionCharts HTTP client, HTML parser
graph/      LangGraph state, nodes, routes, and graph assembly
memory/     Local SQLite checkpoint database created at runtime
schemas/    Dataclasses shared across the application
tools/      Data acquisition, date resolution, and analysis tools
test/       Offline unit tests and integration-oriented test scripts
```



## Requirements

- Python 3.12+
- A DeepSeek API key compatible with the OpenAI Python SDK
- Playwright Chromium browser binaries

Install dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

Create a `.env` file in the project root:

```env
DEEPSEEK_API_KEY=your_api_key_here
```

Do not commit `.env`, `venv/`, or the local SQLite memory database.

## Run

```powershell
python -m run_graph_agent
```

Example requests:

```text
分析 TSLA 2026-08-21 的 GEX 和 DEX
分析特斯拉下周五的信息
再帮我看一下 OI 并分析
再详细解释一下
更新一下数据，再次分析
```

Use `exit`, `quit`, or `退出` to close the CLI cleanly.

## Memory and Cache Behavior



### Conversation memory

LangGraph checkpoints are stored in:

```text
memory/option_agent_checkpoints.db
```

The default CLI uses the `local-option-session` thread ID. With the same thread ID, the agent can recover its recent conversation, running summary, and last successful structured request after restart.

When raw conversation history reaches 12 messages, the agent summarizes older turns and keeps the most recent four raw messages. The summary reduces the context sent to the request-parsing LLM; old checkpoints may still remain in SQLite for recovery and debugging.

### Option-chain cache

The in-memory cache key is:

```text
ticker + expiration
```

Normal repeated analysis requests within five minutes reuse the parsed option chain. The cache is intentionally cleared when the Python process exits so a new run defaults to freshly retrieved market data.

Requests that explicitly ask to refresh, fetch the latest data, or re-fetch the option chain set `force_refresh=True` and bypass the cache.

## Tests

The following tests run offline: they do not call DeepSeek, launch a browser, use cookies, or request OptionCharts.

```powershell
python -m test.test_option_chain_cache
python -m test.test_option_chain_tool_cache
python -m test.test_graph_routing
python -m test.test_natural_date_resolver
```

The project also contains live/integration-oriented scripts under `test/`. Run those only when you intentionally want to use the configured external services.

## Current Limitations

- The CLI is a local, single-user interface.
- Cache metadata such as exact fetch timestamp is not yet shown in final answers.
- Relative-date support is intentionally limited to the expressions listed above.
- Network failures and LLM timeouts do not yet have a retry policy.
- Native LLM tool calling, MCP exposure, and a FastAPI/web interface are planned for V3.

## V3 Direction

- Native LLM Tool Calling
- MCP server packaging for reusable analysis tools
- FastAPI service and frontend integration
- More robust retry, timeout, and observability behavior
- Broader natural-language date resolution and explicit data freshness metadata

