# Implementation Plan: US-04: Stage 4 — Pipeline Engine & Standardized Event Streaming Contract

**User Story**: US-04: Stage 4 — Pipeline Engine & Standardized Event Streaming Contract  
**Parent Epic**: #23  
**GitHub Issue**: #26  
**Requirements**: SPEC P-1–P-5, SPEC §7.1, EVALS §4.1

---

## Tasks
- [ ] Implement support/pipeline.py yielding events (trace, stage, step, llm, tool_call, tool_result, final, error)
- [ ] Extract ADK events (get_function_calls, get_function_responses, is_final_response, usage_metadata)
- [ ] Unwrap {result: ...} JSON envelopes and decode JSON-string arguments
- [ ] Implement runs/<turn_id>.json writer adhering to EVALS §4.1 schema
- [ ] Add --events flag to support/cli.py printing raw NDJSON
- [ ] Verify Stage 4 Prove it checks
---

## Acceptance Criteria
- [ ] support.cli --events emits valid newline-delimited JSON events.
- [ ] Event payloads match SPEC §7.1 schema exactly.
- [ ] runs/<turn_id>.json contains timestamp, userId, latency, tokens, cost, toolCalls, and final reply.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
