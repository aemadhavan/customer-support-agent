# US-05: Stage 5 — Arize Phoenix Observability & Unified Trace Tree

- **Parent Epic**: [Issue #23](https://github.com/aemadhavan/lumina/issues/23)
- **GitHub Issue**: [Issue #27](https://github.com/aemadhavan/lumina/issues/27)
- **Status**: Backlog
- **Requirements Satisfied**: SPEC O-1–O-4, SPEC §10

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task US-05.1 | Launch Arize Phoenix service on port 6006 with persistent storage | Backlog |
| Task US-05.2 | Implement support/telemetry.py configuring TracerProvider with OTLP exporter to http://localhost:6006/v1/traces | Backlog |
| Task US-05.3 | Instrument Google GenAI via GoogleGenAIInstrumentor().instrument() | Backlog |
| Task US-05.4 | Wrap pipeline execution inside root span agent.turn (kind CHAIN) | Backlog |
| Task US-05.5 | Emit trace event containing trace_id and navigable UI URL http://localhost:6006/traces/<trace_id> | Backlog |
| Task US-05.6 | Verify Stage 5 Prove it checks (span hierarchy: agent.turn -> invoke_agent -> call_llm -> execute_tool) | Backlog |
## Documents in this Folder

- [implementation_plan.md](./implementation_plan.md): Architectural design decisions and verification steps.
