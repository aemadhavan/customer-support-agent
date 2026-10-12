# Implementation Plan: US-02 Stage 2 — MCP Toolbox for Databases & Authorization in SQL

**User Story**: US-02 MCP Toolbox for Databases & Authorization in SQL  
**Parent Epic**: Assignment 04: Customer Support — Multi-Agent Systems & Protocol Layer Orchestration  
**Priority**: P1  
**Goal**: Define database access exclusively through Model Context Protocol (MCP) tools in `mcp_toolbox/tools.yaml`. Enforce order ownership at the SQL query level, prevent any database mutation to `customer_orders`, and expose tools over MCP Toolbox HTTP/SSE.

---

## User Review Required

> [!IMPORTANT]
> **Stage 2 Design Decision (*You decide*)**
> Where is "a customer may only see their own orders" enforced?
> - **In SQL / Tool layer (Correct per SPEC M-4/M-5)**: `WHERE customer_email = $n`. The database will not return another user's rows regardless of what prompt is given.
> - **In System Prompt (Failure precedent in reference build)**: Instructions saying "only access this user's data" can be bypassed via prompt injection.

---

## Proposed Changes

```
US-02: MCP Toolbox for Databases & Authorization in SQL
├── Task 2.1: Create mcp_toolbox/tools.yaml with postgres source
├── Task 2.2: Add get-order-status tool with strict WHERE order_id = $1 AND customer_email = $2
├── Task 2.3: Add find-customer-orders tool with WHERE customer_email = $1 ORDER BY order_date DESC
├── Task 2.4: Add action-log tool for recording requested order changes
├── Task 2.5: Verify no update/delete/insert tools exist for customer_orders (T-MUTATE red line)
└── Task 2.6: Test tool invocation via curl/toolbox-core
```

---

## Acceptance Criteria

- [ ] `get-order-status` invoked with `{"order_id": 3, "customer_email": "alice.jones@example.com"}` returns Order 3 details.
- [ ] `get-order-status` invoked with `{"order_id": 5, "customer_email": "alice.jones@example.com"}` returns empty/null.
- [ ] No tool exists that mutates `customer_orders`.
