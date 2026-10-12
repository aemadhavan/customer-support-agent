# US-01: Stage 1 — Database Schema, Reset Harness & Seed Verification

- **Parent Epic**: Assignment 04: Customer Support — Multi-Agent Systems & Protocol Layer Orchestration
- **Status**: In Progress
- **Priority**: P1 (Urgent)
- **Requirements Satisfied**: SPEC M-1, M-7, M-8, EVALS §2

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task 1.1 | Define PostgreSQL schema in `db/schema.sql` (`users`, `customer_orders`, `actions_log`) | Backlog |
| Task 1.2 | Add `CHECK` constraint on `actions_log.action_type` enum values (M-7) | Backlog |
| Task 1.3 | Add index on `customer_orders(customer_email)` for optimized customer filtering | Backlog |
| Task 1.4 | Author `db/seed.sql` with exact 10 users and 17 orders in EVALS §2 sequential order | Backlog |
| Task 1.5 | Implement fast programmatic reset harness `db/reset.py` | Backlog |
| Task 1.6 | Execute Stage 1 *Prove it* checks and record findings in `BUILD_LOG.md` | Backlog |

## Documents in this Folder

- [`implementation_plan.md`](./implementation_plan.md): Architectural design decisions, trade-offs, and verification steps for Stage 1.
