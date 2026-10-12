# US-07: Stage 7 — In-Process Scope Guardrail Agent & Calibration

- **Parent Epic**: [Issue #23](https://github.com/aemadhavan/lumina/issues/23)
- **GitHub Issue**: [Issue #29](https://github.com/aemadhavan/lumina/issues/29)
- **Status**: Backlog
- **Requirements Satisfied**: SPEC GR-1–GR-4

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task US-07.1 | Implement guards/guardrail.py as an ADK agent returning {decision: allow | block, reasoning: ...} | Backlog |
| Task US-07.2 | Author calibrated system prompt defining shop scope with domain-specific positive/negative exemplars | Backlog |
| Task US-07.3 | Enforce fresh session per check (GR-3); raise error if verdict is unparseable (GR-4) | Backlog |
| Task US-07.4 | Add guardrail.check span to pipeline telemetry | Backlog |
| Task US-07.5 | Calibrate across legitimate (L01-L30) and off-topic (F01-F10) gold sets to satisfy G-ENFORCE | Backlog |
| Task US-07.6 | Verify Stage 7 Prove it checks (F01 blocked; L06, L29, M05 pass) | Backlog |
## Documents in this Folder

- [implementation_plan.md](./implementation_plan.md): Architectural design decisions and verification steps.
