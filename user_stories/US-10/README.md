# US-10: Stage 10 — Automated Eval Runner, SLA Thresholds & Gold Set Verification

- **Parent Epic**: [Issue #23](https://github.com/aemadhavan/lumina/issues/23)
- **GitHub Issue**: [Issue #32](https://github.com/aemadhavan/lumina/issues/32)
- **Status**: Backlog
- **Requirements Satisfied**: EVALS §1–§5, THRESHOLDS.md

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task US-10.1 | Transcribe 7 gold test sets from EVALS §3 into eval/gold/*.json | Backlog |
| Task US-10.2 | Implement eval/run.py to reset DB, clear Mem0, execute test suites, collect traces, and evaluate SLA metrics | Backlog |
| Task US-10.3 | Output reports/eval.json adhering to EVALS §4.2 schema with exit codes 0, 1, or 2 | Backlog |
| Task US-10.4 | Verify Gate 5 human review: verify one successful turn and one failing turn (runs/failing/) | Backlog |
| Task US-10.5 | Verify Stage 10 Prove it check (python -m eval.run exits with code 0) | Backlog |
## Documents in this Folder

- [implementation_plan.md](./implementation_plan.md): Architectural design decisions and verification steps.
