# TestForge — Test Plan

## Scope

This test plan covers the TestForge Store API v1.0.0. It defines what will be tested, the approach, entry/exit criteria, and tools used.

---

## Features in Scope

| Feature | Endpoints |
|---|---|
| Health check | `GET /health` |
| List products | `GET /api/v1/products` |
| Get product by ID | `GET /api/v1/products/{id}` |
| Create product | `POST /api/v1/products` |
| Update product | `PUT /api/v1/products/{id}` |
| Delete product | `DELETE /api/v1/products/{id}` |
| User registration | `POST /api/v1/auth/register` |
| User login | `POST /api/v1/auth/login` |
| List orders | `GET /api/v1/orders` |
| Place order | `POST /api/v1/orders` |

---

## Features Out of Scope

- Payment processing (not implemented)
- Email notifications (not implemented)
- Admin roles and RBAC (not implemented)
- Performance and load testing
- Browser UI testing

---

## Test Approach

**Phase 1 — Unit Tests:** Schema validators, service business rules, JWT helpers.

**Phase 2 — Integration Tests:** Full HTTP cycles, CRUD workflows, auth enforcement, pagination.

**Phase 3 — Negative/Boundary Tests:** Empty strings, zero/negative values, boundary integers, wrong types, missing fields, duplicates.

**Phase 4 — Security Tests:** Unauthenticated access, forged tokens, SQL-style injection, oversized inputs, safe error responses.

**Phase 5 — Regression Tests:** One test per confirmed defect (DEFECT-001, -002, -003).

---

## Entry Criteria

- Application installs and starts from documented commands
- All dependencies are pinned
- Test database is isolated (in-memory) and reset between tests

## Exit Criteria

- All 130 tests pass
- No tests suppressed or weakened
- Code coverage ≥ 80% for `app/`
- Ruff reports zero errors
- GitHub Actions workflow passes

---

## Tools

| Tool | Version | Purpose |
|---|---|---|
| pytest | 8.3.4 | Test runner |
| pytest-asyncio | 0.24.0 | Async test support |
| pytest-cov | 6.0.0 | Coverage measurement |
| pytest-html | 4.1.1 | HTML report |
| pytest-json-report | 1.5.0 | Machine-readable JSON |
| httpx | 0.28.1 | Async HTTP client |
| ruff | 0.8.4 | Linting |

---

## Risk Register

| Risk | Mitigation |
|---|---|
| bcrypt/passlib version clash | Use bcrypt directly, pin to 4.0.1 |
| pytest-asyncio event loop issues | `asyncio_mode=auto`, function-scoped fixtures |
| Test isolation failure | Fresh engine per test via fixture; verified |
| Third-party deprecation warnings | Noted; not application defects |
