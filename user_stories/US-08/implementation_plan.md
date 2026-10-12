# Implementation Plan: US-08: Stage 8 — A2A Data Masker & Mem0 Cloud Semantic Memory Integration

**User Story**: US-08: Stage 8 — A2A Data Masker & Mem0 Cloud Semantic Memory Integration  
**Parent Epic**: #23  
**GitHub Issue**: #30  
**Requirements**: SPEC K-1–K-3, R-1–R-6

---

## Tasks
- [x] Implement A2A Data Masker service (guards/masker.py on :10003) redacting PII without altering case/whitespace
- [x] Implement support/memory.py using mem0ai client
- [x] Add pipeline recall step before agent (span memory.recall, kind RETRIEVER, filter by score & chars)
- [x] Add pipeline save step after masker (span memory.save, customer message only, unblocked turns only)
- [x] Ensure agent has NO internal memory tool (R-6)
- [x] Verify Stage 8 Prove it checks (Diana preference saved & recalled; attacks not saved; PII masked)
---

## Acceptance Criteria
- [x] Diana preferences are recalled in subsequent turns with score >= T-MEM-MINSCORE.
- [x] Blocked turns execute zero memory.save calls.
- [x] Data Masker redacts PII and reports changed fields without case alteration.
---

## Definition of Done
- Fully tested, verified against technical checks, and logged in BUILD_LOG.md.
