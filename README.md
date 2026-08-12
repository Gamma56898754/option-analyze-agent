# Option Analyze Agent

An educational options-analysis agent that turns a natural-language request into a validated analysis workflow. It retrieves an option chain, performs deterministic GEX, DEX, open-interest, and max-pain calculations, then uses an LLM to explain the calculated output.

> **Project status:** V1 — a linear, single-request command-line workflow. LangGraph orchestration, persistence, caching, native tool calling, and MCP exposure are planned improvements.

## Why this project

LLMs are useful for interpreting a user's request and explaining results, but they should not invent market data or perform unverified financial calculations. This project separates those responsibilities:

- The **LLM** converts user language into a constrained request and explains supplied calculation results.
- **Typed schemas, validators, data tools, and analyzers** fetch, parse, validate, and calculate deterministic outputs.

## Current capabilities

- Browser-session and HTTP-client reuse during an application run.
- Option expiration resolution and validation.
- HTML option-chain parsing into typed option-contract schemas.
- Deterministic Gamma Exposure (GEX) analysis.
- Deterministic Delta Exposure (DEX) analysis.
- Open Interest (OI) analysis.
- Max Pain analysis.
- Natural-language request parsing into `AnalysisRequest`.
- Request validation before analysis tools run.
- Structured result formatting before LLM interpretation.

## Architecture

```text
User input
  -> LLMAgent: convert language to AnalysisRequest
  -> RequestValidator
  -> AnalysisRunner
       -> OptionChainTool
       -> GEX / DEX / OI / MaxPain tools
  -> ResultFormatter
  -> LLMAgent: explain calculated results
```

```text
data/       Browser session, option-data client, HTML parser
schemas/    Typed request, market, option-chain, and analysis-result objects
analysis/   Deterministic GEX, DEX, OI, and Max Pain calculations
tools/      Interfaces around data access and analyzers
core/       Runtime resource ownership, request validation, orchestration
agent/      LLM request parsing and result explanation
test/       Local executable checks and integration scripts
```

## Requirements

- Python 3.12+
- A DeepSeek API key
- Playwright Chromium browser binaries
- Access to the external option-data source used by `OptionChartClient`

## Setup

From the repository root in Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
```

Open `.env` and set your own API key:

```text
DEEPSEEK_API_KEY=your_key_here
```

Never commit `.env`, browser cookies, sessions, or account data.

## Run

```powershell
python test/test_llm_agent.py
```

V1 accepts one user request, prints one answer, and exits. It does not yet provide multi-turn conversation memory or cross-run persistence.

Example request:

```text
Analyze TSLA GEX and open interest for 2026-08-21.
```

## Local verification

Run from the repository root:

```powershell
python test/test_analysis_runner.py
python test/test_llm_agent.py
```

Some checks use live browser automation and an external data source. Results can vary with market availability, upstream page changes, network conditions, and session state.

## Limitations and safety

- This repository is for educational and research purposes only. It is not investment advice.
- Results depend on external option-chain data and should not be treated as complete, real-time, or error-free market information.
- The LLM is limited to interpreting calculated results; it should not invent numerical values or market data.
- V1 is synchronous, terminal-only, and handles one request per program run.

## Roadmap

- [ ] LangGraph State, Nodes, Edges, and Routing
- [ ] Option-chain cache and request/result persistence
- [ ] Error handling, retries, and regression tests
- [ ] Native LLM tool calling
- [ ] RAG-backed options strategy knowledge with citations
- [ ] MCP server exposing typed analysis tools
- [ ] FastAPI service, Docker, and deployment documentation

## License

No license has been selected yet. Do not assume permission to reuse this code until a license is added.
