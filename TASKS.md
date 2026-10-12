# Assignment 4: Customer Support Multi-Agent Systems Task Tracker

> **Assignment 4: Customer Support** (FDE Agent Engineering Bootcamp | Cohort 2026-03)  
> Instructor: Hamza Farooq  
> **GitHub Project**: [FDE View 1 (Project 5)](https://github.com/users/aemadhavan/projects/5)  
> **Status Overview**: `0 / 10 Stages Completed` (Stage 1 In Progress)

---

## 📊 Quick Status Dashboard

| User Story | Stage Title | Spec Requirements | Status | Progress |
|---|---|---|---|---|
| **US-01** | Stage 1: Database Schema, Reset Harness & Seed Verification | M-1, M-7, M-8, EVALS §2 | 🟢 Completed | 100% |
| **US-02** | Stage 2: MCP Toolbox for Databases & SQL Authorization | M-2, M-3, M-4, M-6 | 🟢 Completed | 100% |
| **US-03** | Stage 3: Support Agent (ADK LlmAgent) & Bound Session | M-5, SPEC §5.2 | 🟢 Completed | 100% |
| **US-04** | Stage 4: Pipeline Generator & Event Streaming Contract | P-1–P-5, SPEC §7.1, EVALS §4.1 | 🟢 Completed | 100% |
| **US-05** | Stage 5: Arize Phoenix Tracing & Unified Trace Tree | O-1–O-4, SPEC §10 | 🟢 Completed | 100% |
| **US-06** | Stage 6: Deterministic Sanitizer & A2A Security Judge | S-1, S-2, J-1–J-4, P-3, P-4 | 🟢 Completed | 100% |
| **US-07** | Stage 7: Scope Guardrail Agent & Prompt Calibration | GR-1–GR-4 | 🟢 Completed | 100% |
| **US-08** | Stage 8: A2A Data Masker & Mem0 Cloud Semantic Memory | K-1–K-3, R-1–R-6 | 🟢 Completed | 100% |
| **US-09** | Stage 9: Streaming FastAPI Web Backend & UI Dashboard | W-1–W-5, SPEC §7.2 | 🟢 Completed | 100% |
| **US-10** | Stage 10: Automated Eval Runner & SLA Thresholds | EVALS §1–§5, THRESHOLDS | ⚪ Pending | 0% |

---

## Stage 1 / US-01: The Database, Schema & Reset Harness
- [x] **Task 1.1**: Define PostgreSQL schema in `db/schema.sql` (`users`, `customer_orders`, `actions_log`).
- [x] **Task 1.2**: Add `CHECK` constraint on `actions_log.action_type` for valid action enums (`CANCEL_ORDER`, `RETURN_ORDER`, `UPDATE_ADDRESS`, `UPDATE_PREFERENCE`, `UPDATE_PROFILE`).
- [x] **Task 1.3**: Add index on `customer_orders(customer_email)` for optimized customer query lookups.
- [x] **Task 1.4**: Author `db/seed.sql` loading the 10 users and 17 orders in exact sequential order (EVALS §2).
- [x] **Task 1.5**: Implement fast programmatic reset harness `db/reset.py` (drops tables, seeds data, restarts SERIAL sequences).
- [x] **Task 1.6**: Run *Prove it* checks (`count(*) from users` == 10; orders 1-17 intact; invalid action type causes CHECK failure).

## Stage 2 / US-02: MCP Toolbox for Databases & Access Control
- [x] **Task 2.1**: Author `mcp_toolbox/tools.yaml` with PostgreSQL database connection.
- [x] **Task 2.2**: Declare read tool `get-order-status(order_id, customer_email)` filtering on `WHERE order_id = $1 AND customer_email = $2`.
- [x] **Task 2.3**: Declare read tool `find-customer-orders(customer_email)` filtering on `WHERE customer_email = $1 ORDER BY order_date DESC`.
- [x] **Task 2.4**: Declare write tool `action-log(user_email, action_type, parameters)`.
- [x] **Task 2.5**: Verify toolset contains ZERO mutation tools targeting `customer_orders` (red-line `T-MUTATE`).
- [x] **Task 2.6**: Run Toolbox server on port 5000 (`npx @toolbox-sdk/server --config mcp_toolbox/tools.yaml --enable-api --address 127.0.0.1 --port 5000`).
- [x] **Task 2.7**: Run *Prove it* checks (Alice gets Order 3; Alice gets nothing for Order 5).

## Stage 3 / US-03: Support Agent & Bound Session Authentication
- [x] **Task 3.1**: Implement ADK `LlmAgent` using Gemini in `support/agent.py`.
- [x] **Task 3.2**: Load `toolbox-core` toolset with session's `customer_email` parameter bound (model cannot alter).
- [x] **Task 3.3**: Implement `InMemorySessionService` and user login validation against `users` table.
- [x] **Task 3.4**: Create interactive CLI loop in `support/cli.py`.
- [x] **Task 3.5**: Run *Prove it* checks (Alice Order 3 -> SHIPPED; Alice Order 5 -> not found; prompt injection for Bob fails).

## Stage 4 / US-04: Pipeline Engine & Standardized Event Streaming Contract
- [x] **Task 4.1**: Create `support/pipeline.py` async generator yielding SPEC §7.1 event contracts (`trace`, `stage`, `step`, `llm`, `tool_call`, `tool_result`, `final`, `error`).
- [x] **Task 4.2**: Extract tool calls, responses, and tokens from ADK runtime events.
- [x] **Task 4.3**: Unwrap `{"result": "..."}` JSON string responses and decode JSON arguments.
- [x] **Task 4.4**: Implement `runs/<turn_id>.json` logger adhering to EVALS §4.1 schema.
- [x] **Task 4.5**: Add `--events` CLI flag streaming NDJSON to stdout.
- [x] **Task 4.6**: Run *Prove it* checks (validate event sequence and `runs/<turn_id>.json` payload).

## Stage 5 / US-05: Arize Phoenix Observability & Unified Trace Tree
- [x] **Task 5.1**: Start Arize Phoenix service on port 6006 with persistent storage.
- [x] **Task 5.2**: Create `support/telemetry.py` with OTLP trace exporter to `http://localhost:6006/v1/traces`.
- [x] **Task 5.3**: Instrument Google GenAI calls with `GoogleGenAIInstrumentor().instrument()`.
- [x] **Task 5.4**: Wrap full message turn inside root span `agent.turn` (kind `CHAIN`).
- [x] **Task 5.5**: Emit `trace` event with trace ID and clickable URL `http://localhost:6006/traces/<id>`.
- [x] **Task 5.6**: Run *Prove it* checks (verify span tree hierarchy: `agent.turn` -> `invoke_agent` -> `call_llm` -> `execute_tool`).

## Stage 6 / US-06: Deterministic Input Sanitizer & A2A Security Judge
- [x] **Task 6.1**: Implement regex input sanitizer in `guards/sanitizer.py` (permit apostrophes & standard text; block obvious exploit syntax).
- [x] **Task 6.2**: Implement A2A Security Judge service in `guards/judge.py` on port 10002 with agent card.
- [x] **Task 6.3**: Add pattern evaluation returning `{verdict: "allow" | "block", reason: "..."}`.
- [x] **Task 6.4**: Integrate into pipeline before agent: spans `security.sanitize` and `security.a2a_judge`.
- [x] **Task 6.5**: Implement fail-loud error handling (P-4) and immediate block termination (P-3).
- [x] **Task 6.6**: Run *Prove it* checks (X01 blocked; L02 & L04 pass; stopped Judge throws error and records `runs/failing/`).

## Stage 7 / US-07: In-Process Scope Guardrail Agent & Calibration
- [x] **Task 7.1**: Implement in-process ADK Guardrail agent in `guards/guardrail.py` returning `{decision, reasoning}`.
- [x] **Task 7.2**: Calibrate domain-specific prompt for shop boundaries with positive/negative examples.
- [x] **Task 7.3**: Enforce fresh session per check and fail-loud unparseable decision handling.
- [x] **Task 7.4**: Add `guardrail.check` span to pipeline telemetry.
- [x] **Task 7.5**: Run *Prove it* checks across legitimate (L01-L30) and off-topic (F01-F10) sets to verify `G-ENFORCE`.

## Stage 8 / US-08: A2A Data Masker & Mem0 Cloud Semantic Memory Integration
- [x] **Task 8.1**: Implement A2A Data Masker service in `guards/masker.py` on port 10003 with agent card.
- [x] **Task 8.2**: Redact outbound PII without altering casing or whitespace, reporting changed fields.
- [x] **Task 8.3**: Implement Mem0 client in `support/memory.py`.
- [x] **Task 8.4**: Add pre-agent `recall` step (span `memory.recall`, kind `RETRIEVER`, score >= `T-MEM-MINSCORE`).
- [x] **Task 8.5**: Add post-masker `save` step (span `memory.save`, customer message only, unblocked turns only).
- [x] **Task 8.6**: Run *Prove it* checks (Diana's preference saved & recalled; attacks not saved; PII masked).

## Stage 9 / US-09: Streaming FastAPI Web Backend & Reactive Dashboard UI
- [x] **Task 9.1**: Build `support/web.py` (FastAPI) streaming NDJSON on `POST /api/chat`.
- [x] **Task 9.2**: Expose `GET /health` and session management.
- [x] **Task 9.3**: Build reactive single-page frontend (`web/index.html`) with token streaming.
- [x] **Task 9.4**: Implement real-time inspector rail (step latencies, executed SQL, tool results, recalled memory, Phoenix link).
- [x] **Task 9.5**: Run *Prove it* checks (`curl -sN` line-by-line streaming; verify event stream parity with CLI `--events`).

## Stage 10 / US-10: Automated Eval Runner, SLA Thresholds & Gold Set Verification
- [ ] **Task 10.1**: Transcribe EVALS §3 gold sets into `eval/gold/*.json`.
- [ ] **Task 10.2**: Implement `eval/run.py` executing all 7 test suites, resetting DB, and clearing Mem0.
- [ ] **Task 10.3**: Parse Phoenix traces and `runs/*.json` logs to calculate all `T-*` metrics.
- [ ] **Task 10.4**: Generate `reports/eval.json` with gates 1 through 5.
- [ ] **Task 10.5**: Perform Gate 5 trajectory verification (one successful run, one failing run from `runs/failing/`).
- [ ] **Task 10.6**: Run *Prove it* check (`python -m eval.run` exits with code 0).
