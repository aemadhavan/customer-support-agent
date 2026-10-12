# Implementation Plan: US-03: Stage 3 — Support Agent (ADK LlmAgent) & Bound Session Authentication

**User Story**: US-03: Stage 3 — Support Agent (ADK LlmAgent) & Bound Session Authentication  
**Parent Epic**: #23  
**GitHub Issue**: #33  
**Requirements**: SPEC M-5, SPEC §5.2

---

## Tasks
- [ ] Implement support/agent.py defining ADK LlmAgent with domain instructions and tool declarations
- [ ] Integrate toolbox-core toolset loader binding customer_email parameter directly from authenticated user session
- [ ] Implement authentication check against users table with InMemorySessionService
- [ ] Implement bare interactive CLI loop in support/cli.py for direct interaction
- [ ] Verify Stage 3 Prove it checks (Alice Order 3 -> SHIPPED; Alice Order 5 -> not found)
---

## Acceptance Criteria
- [ ] Agent answers Alice about Order 3 correctly.
- [ ] Agent answers not found on your account for Order 5; zero Bob info leaked.
- [ ] Agent cannot override the bound session email even when prompted.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
