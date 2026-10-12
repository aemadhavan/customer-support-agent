# US-02: Stage 2 — MCP Toolbox for Databases & Authorization in SQL

- **Parent Epic**: Assignment 04: Customer Support — Multi-Agent Systems & Protocol Layer Orchestration
- **Status**: Backlog
- **Priority**: P1 (Urgent)
- **Requirements Satisfied**: SPEC M-2, M-3, M-4, M-6

## Subtasks

| Task ID | Title | Status |
|---|---|---|
| Task 2.1 | Author `mcp_toolbox/tools.yaml` with PostgreSQL database connection | Backlog |
| Task 2.2 | Declare read tool `get-order-status(order_id, customer_email)` filtering on `order_id = $1 AND customer_email = $2` | Backlog |
| Task 2.3 | Declare read tool `find-customer-orders(customer_email)` filtering on `customer_email = $1 ORDER BY order_date DESC` | Backlog |
| Task 2.4 | Declare write tool `action-log(user_email, action_type, parameters)` | Backlog |
| Task 2.5 | Verify toolset contains ZERO mutation tools targeting `customer_orders` (red-line `T-MUTATE`) | Backlog |
| Task 2.6 | Run Toolbox server on port 5000 (`npx @toolbox-sdk/server --config mcp_toolbox/tools.yaml --enable-api --address 127.0.0.1 --port 5000`) | Backlog |
| Task 2.7 | Run *Prove it* checks (Alice gets Order 3; Alice gets nothing for Bob's Order 5) | Backlog |

## Documents in this Folder

- [`implementation_plan.md`](./implementation_plan.md): Architectural design decisions and verification steps for Stage 2.
