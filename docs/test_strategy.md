# TestForge — Test Strategy

## Purpose

This document describes the testing approach for the TestForge Store API. It explains what is tested, why, and how to interpret the results. It is intended to support technical interviews and to help a new engineer reproduce the test suite from scratch.

---

## Test Objectives

1. Confirm every endpoint behaves correctly for valid inputs.
2. Confirm invalid, missing, out-of-range, and unexpected inputs are rejected safely.
3. Verify authentication and authorisation rules are enforced.
4. Prevent regressions: every fixed defect has a test that fails if the defect is reintroduced.
5. Measure how much of the application code is exercised by the test suite.
6. Produce readable, machine-parseable outputs usable in CI and a dashboard.

---

## Test Categories

### Unit Tests (`tests/unit/`)

**What they test:** Individual functions and classes in isolation — Pydantic schema validators, service business rules, JWT token helpers.

**Why this matters:** These tests run fast and pinpoint the exact function that contains a defect. They do not depend on HTTP routing, the database engine, or external services.

**Coverage goal:** Every branch of a business rule validator should be covered.

---

### Integration Tests (`tests/integration/`)

**What they test:** Full HTTP request/response cycles using HTTPX's `AsyncClient` against a live FastAPI application backed by an isolated in-memory SQLite database.

**Why this matters:** A unit test that passes does not guarantee the router, schema, service, and database work together correctly. Integration tests catch wiring errors.

**Coverage goal:** All CRUD workflows for every endpoint, including happy paths, not-found cases, and common validation failures.

---

### Regression Tests (`tests/regression/`)

**What they test:** One test per confirmed defect. See `docs/defect_log.md` for details.

**Why this matters:** Without regression tests, a fixed defect can silently reappear as the codebase evolves. These tests serve as a permanent safety net.

**Policy:** A regression test is never removed. If a feature changes such that the test no longer applies, the test is updated and the change is documented.

---

### Security-Oriented Tests (`tests/security/`)

**What they test:** Input validation limits, access control enforcement, and safe error responses.

**Why this matters:** An API that accepts oversized inputs, responds to unauthenticated requests, or leaks stack traces in error responses represents a security risk even in a demo application. Testing these behaviours demonstrates awareness of secure coding practices.

---

## Test Design Principles

- **Isolation:** Every test receives a fresh in-memory database. No test depends on state from another.
- **Determinism:** Tests produce the same result on every run, on every machine, in CI.
- **Meaningful names:** Test IDs (e.g. `API-PROD-013`) link to the test catalogue. Names describe the observable behaviour, not the implementation.
- **No suppression:** Tests are never skipped or weakened to achieve a green build. A failing test means the application behaviour does not match the specification.
- **Parametrize where appropriate:** `test_token_subject_preserved_for_various_usernames` tests multiple values in one test function rather than duplicating code.

---

## What Is Not Covered

| Area | Reason |
|---|---|
| Performance / load testing | Outside the scope of this portfolio project |
| Browser / UI end-to-end tests | The application has no server-rendered UI |
| External service integration | No external services are called |
| Production database (PostgreSQL) | Only SQLite is tested; schema compatibility with other dialects is not verified |
| Email delivery | Not implemented |
| Token refresh / revocation | Not in scope; noted as a future improvement |

---

## Running the Tests

```powershell
# Windows — from repo root
.\.venv\Scripts\python.exe -m pytest tests/ -v

# Generate all reports
.\.venv\Scripts\python.exe scripts/run_tests.py
```

```bash
# Linux / macOS / GitHub Actions
python -m pytest tests/ -v
python scripts/run_tests.py
```

---

## Interpreting Results

| Metric | How to read it |
|---|---|
| **Pass rate** | `passed / total * 100`. A 100% pass rate does not prove the application is defect-free; it proves the tested behaviours match expectations. |
| **Coverage %** | Percentage of application statements exercised by at least one test. 85% means 15% of statements were never reached during testing. |
| **Skipped** | No tests are currently marked as skipped in the default suite. |
| **Warnings** | The `DeprecationWarning` from `python-jose` about `datetime.utcnow()` is a third-party library issue, not an application defect. |
