# Option Analysis MCP Server

## Purpose

Expose the existing option-analysis capability as a local MCP tool without
duplicating option-chain retrieval, caching, validation, or calculations.

## Installation

Install the project dependencies after this change:

```powershell
pip install -r requirements.txt
```

## Run locally over stdio

```powershell
python -m mcp_server.option_server
```

The process waits for an MCP client on standard input. Do not use it as a
normal interactive command-line application.

## Tool contract

### `run_option_analysis`

Inputs:

```text
ticker: string
expiration: YYYY-MM-DD
analysis_types: one or more of gex, dex, oi, maxpain
force_refresh: boolean, default false
```

Successful responses are JSON objects containing:

```text
ok: true
trace_id
request
analysis_context
data_quality:
  source
  fetched_at
  cache_state: hit | miss | bypass
  contract_count
  warnings
```

Errors are JSON objects containing `ok: false`, a `trace_id`, and an `error`
object. Error codes are `invalid_request`, `expiration_not_found`,
`market_data_unavailable`, and `internal_error`.

## Cursor configuration

Configure a local MCP server using the project virtual environment:

```json
{
  "mcpServers": {
    "option-analysis": {
      "command": "H:\\Agent_Project\\option_analyze_agent\\venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.option_server"],
      "cwd": "H:\\Agent_Project\\option_analyze_agent"
    }
  }
}
```

## Verification

Run the adapter test without market-data access:

```powershell
python -m test.test_mcp_option_service
```

Run the local MCP integration test after installing the MCP SDK:

```powershell
pytest test/test_mcp_server_integration.py
```

Then start the server through an MCP-compatible client and call
`run_option_analysis` with a known available expiration.
