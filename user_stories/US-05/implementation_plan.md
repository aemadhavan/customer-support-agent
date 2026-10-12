# Implementation Plan: US-05: Stage 5 — Arize Phoenix Observability & Unified Trace Tree

**User Story**: US-05: Stage 5 — Arize Phoenix Observability & Unified Trace Tree  
**Parent Epic**: #23  
**GitHub Issue**: #27  
**Requirements**: SPEC O-1–O-4, SPEC §10

---

## Tasks
- [ ] Launch Arize Phoenix service on port 6006 with persistent storage
- [ ] Implement support/telemetry.py configuring TracerProvider with OTLP exporter to http://localhost:6006/v1/traces
- [ ] Instrument Google GenAI via GoogleGenAIInstrumentor().instrument()
- [ ] Wrap pipeline execution inside root span agent.turn (kind CHAIN)
- [ ] Emit trace event containing trace_id and navigable UI URL http://localhost:6006/traces/<trace_id>
- [ ] Verify Stage 5 Prove it checks (span hierarchy: agent.turn -> invoke_agent -> call_llm -> execute_tool)
---

## Acceptance Criteria
- [ ] Phoenix UI reflects single root agent.turn span per message.
- [ ] Child spans follow SPEC §10 naming and kind hierarchy.
- [ ] Pipeline emits valid, clickable trace URL in trace event.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
