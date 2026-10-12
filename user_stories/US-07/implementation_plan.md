# Implementation Plan: US-07: Stage 7 — In-Process Scope Guardrail Agent & Calibration

**User Story**: US-07: Stage 7 — In-Process Scope Guardrail Agent & Calibration  
**Parent Epic**: #23  
**GitHub Issue**: #29  
**Requirements**: SPEC GR-1–GR-4

---

## Tasks
- [ ] Implement guards/guardrail.py as an ADK agent returning {decision: allow | block, reasoning: ...}
- [ ] Author calibrated system prompt defining shop scope with domain-specific positive/negative exemplars
- [ ] Enforce fresh session per check (GR-3); raise error if verdict is unparseable (GR-4)
- [ ] Add guardrail.check span to pipeline telemetry
- [ ] Calibrate across legitimate (L01-L30) and off-topic (F01-F10) gold sets to satisfy G-ENFORCE
- [ ] Verify Stage 7 Prove it checks (F01 blocked; L06, L29, M05 pass)
---

## Acceptance Criteria
- [ ] False block count on legitimate set <= threshold T-GR-FALSE-BLOCK.
- [ ] Detection rate on off-topic set >= threshold T-GR-DETECT.
- [ ] Guardrail blocks yield user-friendly in-scope explanation.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
