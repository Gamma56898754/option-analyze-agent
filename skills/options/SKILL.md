---

name: option-analysis

description: Analyze US equity option chains with GEX, DEX, open interest, and max pain. Use when the user asks for option-chain analysis, expiration availability, or a follow-up explanation of a recent option analysis.

---

# Option Analysis Skill

## Purpose

Provide structured analysis of a US equity option chain for a specified

ticker and expiration date.

## Supported analysis types

- `gex`: Gamma Exposure
- `dex`: Delta Exposure
- `oi`: Open Interest
- `maxpain`: Max Pain

## Available tool

Use `run_option_analysis` when current option-chain data is needed.

Tool inputs:

- `ticker`: US stock ticker, such as `TSLA`
- `expiration`: expiration date in `YYYY-MM-DD`
- `analysis_types`: one or more supported analysis types
- `force_refresh`: set to `true` only when the user explicitly requests fresh data



## Decision rules

```
Call `run_option_analysis` when the user:

- requests new option-chain analysis
- requests a new indicator
- changes ticker or expiration
- asks to refresh, update, or re-fetch data
- asks an ambiguous question that requires option-market data
- asks for option analysis when no fresh analysis context exists

Within one user turn, do not repeat `run_option_analysis` with the same
arguments after it has returned a result. After a successful tool result,
answer the user unless a distinct tool call is necessary.

A direct answer without a tool call is allowed only when all conditions are true:

- the user clearly asks to explain, summarize, or elaborate
- an existing analysis context is available
- that analysis context is still fresh

Do not use a direct answer when the user requests:

- a new ticker
- a new expiration
- a new analysis type
- a new option-chain analysis
- refreshed or latest data

When analysis context is not fresh:

- do not use, summarize, infer, or rely on old option-market data
- call the tool for any request that requires option analysis

When uncertain whether the user wants a new analysis or only an explanation,
call the tool.
```



## Data constraints

- Option-chain data is time-sensitive.
- Cached option-chain data is valid for at most five minutes.
- Never present expired analysis context as current market data.
- If an expiration is unavailable, provide nearby available expirations.
- Do not invent Greeks, open interest, prices, or market levels.



## Response rules

- State that the analysis is based on data retrieved by the agent.
- Distinguish observed option-chain data from interpretation.
- Clearly surface any material data-quality warning returned by the tool.
- Treat GEX, DEX, OI, and Max Pain as analytical signals, not certainty.
- Include a concise risk disclaimer.
- Do not provide personalized trading instructions or guarantees.

