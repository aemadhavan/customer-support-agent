# Implementation Plan: US-06: Stage 6 — Deterministic Input Sanitizer & A2A Security Judge Service

**User Story**: US-06: Stage 6 — Deterministic Input Sanitizer & A2A Security Judge Service  
**Parent Epic**: #23  
**GitHub Issue**: #28  
**Requirements**: SPEC S-1, S-2, J-1–J-4, P-3, P-4

---

## Tasks
- [ ] Implement guards/sanitizer.py filtering known exploit characters while permitting apostrophes & punctuation
- [ ] Implement A2A Security Judge service (guards/judge.py on :10002) with agent card and A2A endpoint
- [ ] Add deterministic pattern tools returning {verdict: allow | block, reason: ...}
- [ ] Integrate into pipeline before agent: span security.sanitize and security.a2a_judge
- [ ] Implement fail-loud error handling (P-4) and immediate block termination (P-3) with red span in Phoenix
- [ ] Verify Stage 6 Prove it checks (X01 blocked, L02 and L04 pass, stopped Judge causes loud error event)
- [ ] Save failing trajectory in runs/failing/ when Judge is stopped
---

## Acceptance Criteria
- [ ] X01 blocked in < 500 ms; agent stage never executes.
- [ ] L02 and L04 pass without false blocks.
- [ ] Service downtime yields an explicit error event naming the Judge; never fails open.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
