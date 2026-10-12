# US-06: Stage 6 — Deterministic Input Sanitizer & A2A Security Judge Service

- **Parent Epic**: [Issue #23](https://github.com/aemadhavan/lumina/issues/23)
- **GitHub Issue**: [Issue #28](https://github.com/aemadhavan/lumina/issues/28)
- **Status**: Backlog
- **Requirements Satisfied**: SPEC S-1, S-2, J-1–J-4, P-3, P-4

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task US-06.1 | Implement guards/sanitizer.py filtering known exploit characters while permitting apostrophes & punctuation | Backlog |
| Task US-06.2 | Implement A2A Security Judge service (guards/judge.py on :10002) with agent card and A2A endpoint | Backlog |
| Task US-06.3 | Add deterministic pattern tools returning {verdict: allow | block, reason: ...} | Backlog |
| Task US-06.4 | Integrate into pipeline before agent: span security.sanitize and security.a2a_judge | Backlog |
| Task US-06.5 | Implement fail-loud error handling (P-4) and immediate block termination (P-3) with red span in Phoenix | Backlog |
| Task US-06.6 | Verify Stage 6 Prove it checks (X01 blocked, L02 and L04 pass, stopped Judge causes loud error event) | Backlog |
| Task US-06.7 | Save failing trajectory in runs/failing/ when Judge is stopped | Backlog |
## Documents in this Folder

- [implementation_plan.md](./implementation_plan.md): Architectural design decisions and verification steps.
