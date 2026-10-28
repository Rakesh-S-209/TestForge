# TestForge — Test Case Catalogue

Actual results are derived from executed test runs (130 passed, 0 failed).
Last run: Python 3.13.3, Windows 11, 41 s total.

Legend — Severity: P1 Critical | P2 High | P3 Medium | P4 Low

---

## UNIT TESTS — Authentication Service

| ID | Feature | Objective | Precondition | Input | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|---|---|
| AUTH-UNIT-001 | Password hashing | hash_password returns non-empty string | None | "mypassword" | str, len > 0 | Non-empty bcrypt hash | PASS | P2 |
| AUTH-UNIT-002 | Password hashing | Hash differs from plaintext | None | "mypassword" | hash ≠ plain | Confirmed | PASS | P2 |
| AUTH-UNIT-003 | Password verify | Correct password verifies | Valid hash | Matching plain | True | True | PASS | P1 |
| AUTH-UNIT-004 | Password verify | Wrong password rejected | Valid hash | Non-matching | False | False | PASS | P1 |
| AUTH-UNIT-005 | Password hashing | Two hashes of same input differ (salt) | None | "same" x2 | h1 ≠ h2 | Confirmed | PASS | P2 |
| AUTH-UNIT-006 | JWT token | Create and decode round-trip | None | subject="alice" | decode returns "alice" | "alice" | PASS | P1 |
| AUTH-UNIT-007 | JWT token | Tampered token raises ValueError | Valid token | Last 5 chars replaced | ValueError | ValueError raised | PASS | P1 |
| AUTH-UNIT-008 | JWT token | Empty string raises ValueError | None | "" | ValueError | ValueError raised | PASS | P1 |
| AUTH-UNIT-009 | JWT token | Random string raises ValueError | None | "not.a.token" | ValueError | ValueError raised | PASS | P1 |
| AUTH-UNIT-010 | JWT token | Subject preserved for various inputs | None | 4 different usernames | each decoded = input | Confirmed | PASS | P2 |

---

## UNIT TESTS — Product Schema Validation

| ID | Feature | Objective | Input | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|---|
| VAL-PROD-001 | ProductCreate | Valid product passes | name="Widget", price=9.99, stock=10 | No error | Created OK | PASS | P3 |
| VAL-PROD-002 | ProductCreate | Name whitespace stripped | name="  Gadget  " | name="Gadget" | "Gadget" | PASS | P3 |
| VAL-PROD-003 | ProductCreate | Empty name rejected | name="" | ValidationError | Raised | PASS | P2 |
| VAL-PROD-004 | ProductCreate | Whitespace-only name rejected | name="   " | ValidationError | Raised | PASS | P2 |
| VAL-PROD-005 | ProductCreate | Zero price rejected | price=0 | ValidationError | Raised | PASS | P1 — DEFECT-001 |
| VAL-PROD-006 | ProductCreate | Negative price rejected | price=-1.0 | ValidationError | Raised | PASS | P1 |
| VAL-PROD-007 | ProductCreate | Negative stock rejected | stock=-1 | ValidationError | Raised | PASS | P2 |
| VAL-PROD-008 | ProductCreate | Zero stock valid | stock=0 | No error | Created OK | PASS | P3 |
| VAL-PROD-009 | ProductCreate | Minimum price (0.01) valid | price=0.01 | No error | Created OK | PASS | P3 |
| VAL-PROD-010 | ProductCreate | Missing name raises error | (no name) | ValidationError | Raised | PASS | P2 |
| VAL-PROD-011 | ProductCreate | Missing price raises error | (no price) | ValidationError | Raised | PASS | P2 |
| VAL-PROD-012 | ProductCreate | Category normalised | category="ELECTRONICS" | "electronics" | "electronics" | PASS | P3 |
| VAL-PROD-013 | ProductCreate | Non-numeric price rejected | price="free" | ValidationError | Raised | PASS | P2 |
| VAL-PROD-014 | ProductUpdate | Empty update valid | {} | No error | Created OK | PASS | P3 |
| VAL-PROD-015 | ProductUpdate | Price-only update valid | price=49.99 | No error | Created OK | PASS | P3 |
| VAL-PROD-016 | ProductUpdate | Zero price in update rejected | price=0.0 | ValidationError | Raised | PASS | P1 |
| VAL-PROD-017 | ProductUpdate | Negative price in update rejected | price=-5.0 | ValidationError | Raised | PASS | P1 |
| VAL-PROD-018 | ProductUpdate | Negative stock in update rejected | stock=-1 | ValidationError | Raised | PASS | P2 |
| VAL-PROD-019 | ProductUpdate | Blank name in update rejected | name="  " | ValidationError | Raised | PASS | P2 |
| VAL-PROD-020 | ProductUpdate | Category normalised in update | category="GADGETS" | "gadgets" | "gadgets" | PASS | P3 |

---

## UNIT TESTS — Product Service

| ID | Feature | Objective | Input | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|---|
| SVC-PROD-001 | ProductService.list | Empty DB returns total=0 | Empty DB | total=0, items=[] | Confirmed | PASS | P3 |
| SVC-PROD-002 | ProductService.list | page < 1 raises ValueError | page=0 | ValueError | Raised | PASS | P2 — DEFECT-002 |
| SVC-PROD-003 | ProductService.list | page_size > max raises ValueError | page_size=9999 | ValueError | Raised | PASS | P2 |
| SVC-PROD-004 | ProductService.list | page_size=0 raises ValueError | page_size=0 | ValueError | Raised | PASS | P2 — DEFECT-002 |
| SVC-PROD-005 | ProductService.create | Valid product gets integer ID | Valid data | id > 0 | Confirmed | PASS | P2 |
| SVC-PROD-006 | ProductService.get | Correct product returned by ID | Existing ID | Matching product | Confirmed | PASS | P2 |
| SVC-PROD-007 | ProductService.get | Non-existent ID raises LookupError | id=99999 | LookupError | Raised | PASS | P2 |
| SVC-PROD-008 | ProductService.create | Duplicate name raises ValueError | Same name twice | ValueError | Raised | PASS | P2 |
| SVC-PROD-009 | ProductService.update | Price update persists | price=19.99 | updated.price=19.99 | Confirmed | PASS | P2 |
| SVC-PROD-010 | ProductService.update | Non-existent ID raises LookupError | id=99999 | LookupError | Raised | PASS | P2 |
| SVC-PROD-011 | ProductService.delete | Product not found after deletion | Deleted ID | LookupError on get | Raised | PASS | P2 |
| SVC-PROD-012 | ProductService.delete | Non-existent ID raises LookupError | id=99999 | LookupError | Raised | PASS | P2 |
| SVC-PROD-013 | ProductService.list | All created products visible | 5 products | total=5, len=5 | Confirmed | PASS | P2 |
| SVC-PROD-014 | ProductService.list | Page 2 of 3 items returns 1 | page=2, size=2 | len=1, pages=2 | Confirmed | PASS | P2 |
| SVC-PROD-015 | ProductService.list | Category filter works | category="tools" | Only tool products | Confirmed | PASS | P3 |

---

## INTEGRATION TESTS — Health

| ID | Feature | Objective | Input | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|---|
| API-HEALTH-001 | GET /health | Returns 200 | No input | 200 | 200 | PASS | P1 |
| API-HEALTH-002 | GET /health | Body contains status=ok | No input | status="ok" | "ok" | PASS | P1 |
| API-HEALTH-003 | GET /health | Response has app and version | No input | Both keys present | Confirmed | PASS | P2 |

---

## INTEGRATION TESTS — Authentication

| ID | Feature | Objective | Input | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|---|
| API-AUTH-001 | POST /register | Valid registration returns 201 | Valid user data | 201 | 201 | PASS | P1 |
| API-AUTH-002 | POST /register | Response has user fields | Valid user data | id, username, email, is_active | Confirmed | PASS | P1 |
| API-AUTH-003 | POST /register | Duplicate username returns 409 | Same username | 409 | 409 | PASS | P1 |
| API-AUTH-004 | POST /register | Duplicate email returns 409 | Same email | 409 | 409 | PASS | P1 |
| API-AUTH-005 | POST /register | Invalid email format returns 422 | email="not-email" | 422 | 422 | PASS | P2 |
| API-AUTH-006 | POST /login | Valid credentials return 200 | Correct user/pass | 200 | 200 | PASS | P1 |
| API-AUTH-007 | POST /login | Response contains JWT token | Valid credentials | access_token present | Confirmed | PASS | P1 |
| API-AUTH-008 | POST /login | Wrong password returns 401 | Wrong password | 401 | 401 | PASS | P1 |
| API-AUTH-009 | POST /login | Non-existent user returns 401 | Unknown username | 401 | 401 | PASS | P1 |
| API-AUTH-010 | POST /login | Missing password returns 422 | No password | 422 | 422 | PASS | P2 |
| API-AUTH-011 | POST /products | No token returns 401 | No auth header | 401 | 401 | PASS | P1 — DEFECT-003 |
| API-AUTH-012 | POST /products | Forged token returns 401 | Fake JWT | 401 | 401 | PASS | P1 — DEFECT-003 |
| API-AUTH-013 | PUT /products | No token returns 401 | No auth header | 401 | 401 | PASS | P1 — DEFECT-003 |
| API-AUTH-014 | DELETE /products | No token returns 401 | No auth header | 401 | 401 | PASS | P1 — DEFECT-003 |
| API-AUTH-015 | GET /orders | No token returns 401 | No auth header | 401 | 401 | PASS | P1 |

---

## INTEGRATION TESTS — Products

| ID | Feature | Objective | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|
| API-PROD-001 | GET /products | Empty store returns 200 + empty list | 200, items=[] | Confirmed | PASS | P2 |
| API-PROD-002 | GET /products | Response schema has pagination fields | 5 fields | Confirmed | PASS | P2 |
| API-PROD-003 | GET /products | Created product appears in list | total=1 | Confirmed | PASS | P2 |
| API-PROD-004 | GET /products | Pagination page 2 works | 1 item on page 2 | Confirmed | PASS | P2 |
| API-PROD-005 | GET /products | Category filter returns only matches | Only category match | Confirmed | PASS | P2 |
| API-PROD-006 | GET /products | page_size=9999 returns 422 | 422 | 422 | PASS | P2 — DEFECT-002 |
| API-PROD-007 | GET /products/:id | Existing product returns 200 | 200 | 200 | PASS | P2 |
| API-PROD-008 | GET /products/:id | Response matches creation data | Matching fields | Confirmed | PASS | P2 |
| API-PROD-009 | GET /products/:id | Non-existent returns 404 | 404 | 404 | PASS | P2 |
| API-PROD-010 | GET /products/:id | Timestamps in response | created_at + updated_at | Confirmed | PASS | P3 |
| API-PROD-011 | POST /products | Valid creation returns 201 | 201 | 201 | PASS | P1 |
| API-PROD-012 | POST /products | Response has all fields | 7 fields | Confirmed | PASS | P1 |
| API-PROD-013 | POST /products | Zero price returns 422 | 422 | 422 | PASS | P1 — DEFECT-001 |
| API-PROD-014 | POST /products | Negative price returns 422 | 422 | 422 | PASS | P1 |
| API-PROD-015 | POST /products | Empty name returns 422 | 422 | 422 | PASS | P2 |
| API-PROD-016 | POST /products | Negative stock returns 422 | 422 | 422 | PASS | P2 |
| API-PROD-017 | POST /products | Duplicate name returns 409 | 409 | 409 | PASS | P2 |
| API-PROD-018 | POST /products | Missing required fields returns 422 | 422 | 422 | PASS | P2 |
| API-PROD-019 | POST /products | String price returns 422 | 422 | 422 | PASS | P2 |
| API-PROD-020 | POST /products | Zero stock is valid | 201 | 201 | PASS | P3 |
| API-PROD-021 | PUT /products/:id | Price update returns 200 | 200 | 200 | PASS | P1 |
| API-PROD-022 | PUT /products/:id | Updated price in GET response | 49.99 | 49.99 | PASS | P1 |
| API-PROD-023 | PUT /products/:id | Non-existent returns 404 | 404 | 404 | PASS | P2 |
| API-PROD-024 | PUT /products/:id | Zero price returns 422 | 422 | 422 | PASS | P1 |
| API-PROD-025 | PUT /products/:id | Valid stock update | 200, stock=200 | Confirmed | PASS | P2 |
| API-PROD-026 | PUT /products/:id | Rename to taken name returns 409 | 409 | 409 | PASS | P2 |
| API-PROD-027 | PUT /products/:id | Partial update preserves other fields | Only stock changes | Confirmed | PASS | P2 |
| API-PROD-028 | PUT /products/:id | Empty body is valid no-op | 200 | 200 | PASS | P3 |
| API-PROD-029 | DELETE /products/:id | Existing returns 204 | 204 | 204 | PASS | P1 |
| API-PROD-030 | DELETE /products/:id | Deleted product returns 404 on GET | 404 | 404 | PASS | P1 |
| API-PROD-031 | DELETE /products/:id | Non-existent returns 404 | 404 | 404 | PASS | P2 |
| API-PROD-032 | DELETE /products/:id | Deleted product not in list | Not in items | Confirmed | PASS | P2 |
| API-PROD-033 | DELETE /products/:id | Second delete returns 404 | 404 | 404 | PASS | P2 |

---

## INTEGRATION TESTS — Orders

| ID | Feature | Objective | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|
| API-ORD-001 | GET /orders | New user has no orders | total=0 | Confirmed | PASS | P2 |
| API-ORD-002 | POST /orders | Valid order returns 201 | 201 | 201 | PASS | P1 |
| API-ORD-003 | POST /orders | Response has all fields | 6 fields | Confirmed | PASS | P1 |
| API-ORD-004 | GET /orders | Placed order appears | total=1 | Confirmed | PASS | P1 |
| API-ORD-005 | POST /orders | Non-existent product returns 404 | 404 | 404 | PASS | P2 |
| API-ORD-006 | POST /orders | Exceeding stock returns 422 | 422 | 422 | PASS | P2 |
| API-ORD-007 | POST /orders | unit_price matches product | Equal | Confirmed | PASS | P2 |
| API-ORD-008 | POST /orders | New order status is pending | "pending" | "pending" | PASS | P3 |
| API-ORD-009 | POST /orders | No auth returns 401 | 401 | 401 | PASS | P1 |
| API-ORD-010 | POST /orders | Zero quantity returns 422 | 422 | 422 | PASS | P2 |
| API-ORD-011 | GET /orders | User cannot see others' orders | total=0 for other user | Confirmed | PASS | P1 |
| API-ORD-012 | POST /orders | Missing product_id returns 422 | 422 | 422 | PASS | P2 |

---

## REGRESSION TESTS

| ID | Defect | Objective | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|
| REGRESSION-001 | DEFECT-001 | price=0 rejected via API | 422 | 422 | PASS | P1 |
| REGRESSION-001b | DEFECT-001 | price=-1.0 rejected via API | 422 | 422 | PASS | P1 |
| REGRESSION-002 | DEFECT-002 | page_size=0 returns 422, not 500 | 422 | 422 | PASS | P2 |
| REGRESSION-002b | DEFECT-002 | page=0 returns 422, not 500 | 422 | 422 | PASS | P2 |
| REGRESSION-003 | DEFECT-003 | POST without auth returns 401 | 401 | 401 | PASS | P1 |
| REGRESSION-003b | DEFECT-003 | PUT without auth returns 401 | 401 | 401 | PASS | P1 |
| REGRESSION-003c | DEFECT-003 | DELETE without auth returns 401 | 401 | 401 | PASS | P1 |

---

## SECURITY TESTS

| ID | Feature | Objective | Expected | Actual | Status | Sev |
|---|---|---|---|---|---|---|
| SEC-001 | Input length | 300-char name rejected | 422 | 422 | PASS | P2 |
| SEC-002 | SQL injection | Injection string handled safely | 201 or 422, never 500 | Confirmed | PASS | P1 |
| SEC-003 | Pagination | page_size=1000000 rejected | 422 | 422 | PASS | P2 |
| SEC-004 | ID validation | Non-integer product ID returns 422 | 422 | 422 | PASS | P2 |
| SEC-005 | Extra fields | Extra JSON fields ignored | 201, no extra fields in response | Confirmed | PASS | P2 |
| SEC-006 | Auth | Invalid token returns 401 | 401 | 401 | PASS | P1 |
| SEC-007 | Auth | Missing Bearer prefix rejected | 401 | 401 | PASS | P1 |
| SEC-008 | Auth | All write ops require auth | 401 for each | Confirmed | PASS | P1 |
| SEC-009 | Auth | GET /orders requires auth | 401 | 401 | PASS | P1 |
| SEC-010 | Auth | POST /orders requires auth | 401 | 401 | PASS | P1 |
| SEC-011 | Error safety | 404 contains no stack trace | No "Traceback" in body | Confirmed | PASS | P1 |
| SEC-012 | Error safety | 401 contains no system paths | No "Traceback" in body | Confirmed | PASS | P1 |
| SEC-013 | Error safety | 422 has structured detail | detail is list | Confirmed | PASS | P2 |
| SEC-014 | Routing | Unknown URL returns 404 | 404 | 404 | PASS | P2 |
| SEC-015 | Routing | Wrong HTTP method returns 405 | 405 | 405 | PASS | P2 |

---

## Summary

| Category | Total | Passed | Failed | Coverage |
|---|---|---|---|---|
| Unit — Auth | 10 | 10 | 0 | — |
| Unit — Product Schema | 20 | 20 | 0 | — |
| Unit — Product Service | 15 | 15 | 0 | — |
| Integration — Health | 3 | 3 | 0 | — |
| Integration — Auth | 15 | 15 | 0 | — |
| Integration — Products | 33 | 33 | 0 | — |
| Integration — Orders | 12 | 12 | 0 | — |
| Regression | 7 | 7 | 0 | — |
| Security | 15 | 15 | 0 | — |
| **Total** | **130** | **130** | **0** | **85%** |
