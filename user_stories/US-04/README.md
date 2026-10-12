# US-04: Stage 4 — Pipeline Engine & Standardized Event Streaming Contract

- **Parent Epic**: [Issue #23](https://github.com/aemadhavan/lumina/issues/23)
- **GitHub Issue**: [Issue #26](https://github.com/aemadhavan/lumina/issues/26)
- **Status**: Backlog
- **Requirements Satisfied**: SPEC P-1–P-5, SPEC §7.1, EVALS §4.1

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task US-04.1 | Implement support/pipeline.py yielding events (trace, stage, step, llm, tool_call, tool_result, final, error) | Backlog |
| Task US-04.2 | Extract ADK events (get_function_calls, get_function_responses, is_final_response, usage_metadata) | Backlog |
| Task US-04.3 | Unwrap {result: ...} JSON envelopes and decode JSON-string arguments | Backlog |
| Task US-04.4 | Implement runs/<turn_id>.json writer adhering to EVALS §4.1 schema | Backlog |
| Task US-04.5 | Add --events flag to support/cli.py printing raw NDJSON | Backlog |
| Task US-04.6 | Verify Stage 4 Prove it checks | Backlog |
## Documents in this Folder

- [implementation_plan.md](./implementation_plan.md): Architectural design decisions and verification steps.
