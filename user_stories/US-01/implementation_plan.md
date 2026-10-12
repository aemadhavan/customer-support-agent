# Implementation Plan: US-01 Stage 1 — Database Schema, Reset Harness & Seed Verification

**User Story**: US-01 Database Schema, Reset Harness & Seed Verification  
**Parent Epic**: Assignment 04: Customer Support — Multi-Agent Systems & Protocol Layer Orchestration  
**Priority**: P1  
**Goal**: Initialize PostgreSQL tables (`users`, `customer_orders`, `actions_log`), enforce integrity and security constraints (action_type `CHECK`, email index), seed with deterministic order IDs (1-17), and build a fast reset harness for automated grading.

---

## User Review Required

> [!IMPORTANT]
> **Stage 1 Design Decision (*You decide*)**
> How should a run start from a known state?
> - **Option A**: Programmatic SQL reset script (`db/reset.py`) dropping/recreating tables with `RESTART IDENTITY`. Fast (< 500ms) and integrated into test runner.
> - **Option B**: Docker container volume teardown (`docker compose down -v && docker compose up -d`). High isolation, but slower (3-5s).

---

## Proposed Changes

```
US-01: Database Schema, Reset Harness & Seed Verification
├── Task 1.1: db/schema.sql (users, customer_orders, actions_log DDL)
├── Task 1.2: Enforce CHECK constraint on actions_log.action_type
├── Task 1.3: Create index idx_customer_orders_email on customer_orders(customer_email)
├── Task 1.4: db/seed.sql (exact 10 users, 17 orders per EVALS §2)
├── Task 1.5: db/reset.py (idempotent reset script)
└── Task 1.6: Run Stage 1 Prove it commands
```

---

## Acceptance Criteria

- [ ] `select count(*) from users;` returns 10.
- [ ] `select order_id, customer_email, status from customer_orders order by order_id;` matches EVALS §2 table exactly.
- [ ] `insert into actions_log (user_email, action_type, parameters) values ('x', 'RETURN_ITEM', '{}');` fails with a `CHECK` constraint violation.
- [ ] `python db/reset.py` resets database state idempotently in under 1 second.

---

## Verification Plan

1. Execute `python db/reset.py`.
2. Run SQL probes to verify row counts, order IDs, and schema constraints.
3. Validate negative test inserting unauthorized action type.
