# Implementation Plan: US-10: Stage 10 — Automated Eval Runner, SLA Thresholds & Gold Set Verification

**User Story**: US-10: Stage 10 — Automated Eval Runner, SLA Thresholds & Gold Set Verification  
**Parent Epic**: #23  
**GitHub Issue**: #32  
**Requirements**: EVALS §1–§5, THRESHOLDS.md

---

## Tasks
- [ ] Transcribe 7 gold test sets from EVALS §3 into eval/gold/*.json
- [ ] Implement eval/run.py to reset DB, clear Mem0, execute test suites, collect traces, and evaluate SLA metrics
- [ ] Output reports/eval.json adhering to EVALS §4.2 schema with exit codes 0, 1, or 2
- [ ] Verify Gate 5 human review: verify one successful turn and one failing turn (runs/failing/)
- [ ] Verify Stage 10 Prove it check (python -m eval.run exits with code 0)
---

## Acceptance Criteria
- [ ] python -m eval.run runs end-to-end and outputs valid reports/eval.json.
- [ ] Zero authorization leaks (T-AUTH-LEAK = 0) and zero mutation attempts (T-MUTATE = 0).
- [ ] All SLA and quality thresholds in THRESHOLDS.md pass.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
