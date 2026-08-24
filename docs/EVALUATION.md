# V4 Offline Evaluation Suite

## Purpose

These cases verify agent behavior without a DeepSeek API key, Playwright, or
live OptionCharts requests. They use the real LangGraph and deterministic fake
Agent/tool implementations.

## Run

```powershell
pytest test/test_evaluation_suite.py
```

Or run the standalone test module:

```powershell
python -m test.test_evaluation_suite
```

## Acceptance criteria

| Case | Expected behavior |
| --- | --- |
| New analysis | Exactly one tool execution, then a final answer after observation feedback. |
| Fresh explanation | No tool execution; fresh context reaches the Agent. |
| Stale analysis | Old context is withheld and a new tool execution is required. |
| Invalid arguments | A controlled validation answer is returned. |
| Missing expiration | A controlled answer includes nearby available expirations. |
| Market source failure | The same tool stops after two consecutive unavailable-source failures. |
| Duplicate tool call | The second identical call is blocked before execution. |
| Max tool steps | Endless tool selection stops after three attempts. |
| Relative date | "next Friday" resolves deterministically from the supplied market date. |
| Data quality warning | The formatter includes the warning in the Agent-visible context. |

## Latest result

Passed locally on 2026-08-24 with:

```powershell
python -m test.test_evaluation_suite
```

Result: `All V4 offline evaluation cases passed.`
