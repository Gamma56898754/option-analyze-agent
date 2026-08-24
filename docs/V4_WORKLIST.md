# V4 Worklist — Option Skill Platform

## Scope

V4 focuses on making the existing option-analysis capability reusable,

observable, testable, and safely extensible.

Futures analysis and RAG are explicitly out of scope for V4.

## 1. Option Analysis Skill

Status: completed

- [ ] Create `skills/options/SKILL.md`

- [ ] Define supported user intents, inputs, outputs, constraints, and data freshness rules

- [ ] Add a small skill-loading mechanism

- [ ] Make the LLM receive the option-skill instructions when handling option requests

- [ ] Verify that existing option analysis behavior remains unchanged



## 2. Multi-tool Agent Loop

Status: completed

- [ ] Split capabilities into focused tools

- [ ] Add tool observation state

- [ ] Add bounded agent loop with `max_steps`

- [ ] Add duplicate-tool-call protection

- [ ] Add loop and routing tests



## 3. Data Quality and Provenance

Status: completed

- [x] Define `DataQualityReport`

- [x] Record source, fetched time, cache state, contract count, and warnings

- [x] Surface material data-quality warnings in answers

- [x] Add quality-report tests



## 4. MCP Server

Status: completed

- [x] Wrap stable existing option tools as MCP tools

- [x] Reuse existing business logic; do not duplicate analysis calculations

- [x] Add local MCP integration test

- [x] Document MCP tool contracts



## 5. Evaluation Suite

Status: completed

- [x] Create offline evaluation cases

- [x] Evaluate tool selection, routing, freshness, invalid dates, and data-source failures

- [x] Add regression cases for known bugs

- [x] Record evaluation results and acceptance criteria
