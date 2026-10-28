# TestForge — Defect Log

This document records three representative defects used as a controlled demonstration exercise. Each defect was introduced deliberately in an isolated context, verified with a failing test, then fixed and verified with a passing test. The default application code contains **no intentional defects**.

---

## DEFECT-001 — Price Validation: Zero Price Accepted

### Description
The product creation endpoint accepted a price of `0.0`, violating the business rule that all product prices must be strictly greater than zero.

### Impact
A product with a zero price could be ordered, resulting in zero-revenue transactions with no validation error. This would corrupt sales reporting data.

### Root Cause
The `price` field in the original (defective) schema used `ge=0` (greater than or equal to zero) instead of `gt=0` (strictly greater than zero).

**Defective code (schema):**
```python
price: float = Field(..., ge=0)   # WRONG — allows 0
```

**Fixed code:**
```python
price: float = Field(..., gt=0)   # CORRECT — requires > 0
```

### Reproduction
```bash
# With the defective schema, this request would return 201:
curl -X POST /api/v1/products \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Free Widget", "price": 0, "stock": 1, "category": "misc"}'
# Expected: 422  |  Actual (defective): 201
```

### Regression Test
`tests/regression/test_regression.py::TestDefect001PriceValidation`
- `test_zero_price_rejected_via_api` — asserts status 422 for price=0
- `test_negative_price_rejected_via_api` — asserts status 422 for price=-1.0

Both tests pass on the fixed application and would fail if the defect were reintroduced.

---

## DEFECT-002 — Pagination: page_size=0 Caused ZeroDivisionError

### Description
Requesting products with `page_size=0` caused the server to raise a `ZeroDivisionError` when calculating the page count (`ceil(total / 0)`), returning an unhandled HTTP 500 error.

### Impact
Any client (legitimate or malicious) could trigger a server error with a trivial request parameter. This degrades availability and leaks the fact that the server raises unhandled exceptions.

### Root Cause
The page count calculation `math.ceil(total / page_size)` was reached before validating that `page_size > 0`. FastAPI's `Query(ge=1)` constraint now prevents `page_size=0` from reaching the service layer.

**Defective code (router):**
```python
page_size: int = Query(0)   # WRONG — no lower bound
```

**Fixed code (router):**
```python
page_size: int = Query(default_page_size, ge=1, le=max_page_size)
```

Additionally, the service layer also validates:
```python
if effective_size < 1:
    raise ValueError("page_size must be >= 1")
```

This dual-layer validation means the error is caught at the schema boundary and returns a structured 422 rather than propagating to cause a 500.

### Regression Tests
`tests/regression/test_regression.py::TestDefect002PaginationBoundary`
- `test_page_size_zero_returns_422_not_500` — asserts 422, explicitly checks not 500
- `test_page_zero_returns_422_not_500` — asserts 422 for page=0

---

## DEFECT-003 — Authorization: Unauthenticated Product Creation

### Description
The product creation, update, and delete endpoints initially had no authentication requirement. Any HTTP client could create, modify, or delete products without providing a token.

### Impact
Critical. Without authentication on write operations, any anonymous user can modify the product catalogue. This is an access control failure that would be unacceptable in any real deployment.

### Root Cause
The `Depends(get_current_user)` dependency was not added to the `create_product`, `update_product`, and `delete_product` route handlers.

**Defective code (router):**
```python
@router.post("")
async def create_product(data: ProductCreate, session: AsyncSession = Depends(get_session)):
    ...
```

**Fixed code:**
```python
@router.post("")
async def create_product(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
    _current_user: User = Depends(get_current_user),  # ← added
):
    ...
```

### Regression Tests
`tests/regression/test_regression.py::TestDefect003Authorization`
- `test_create_product_without_auth_returns_401`
- `test_update_product_without_auth_returns_401`
- `test_delete_product_without_auth_returns_401`

All three tests confirm that write operations return 401 without a valid token. They would fail immediately if the `Depends(get_current_user)` was removed.

---

## Summary Table

| ID | Description | Severity | Status | Regression Test |
|---|---|---|---|---|
| DEFECT-001 | Zero price accepted by product creation | Medium | Fixed | `TestDefect001PriceValidation` |
| DEFECT-002 | `page_size=0` caused HTTP 500 | Medium | Fixed | `TestDefect002PaginationBoundary` |
| DEFECT-003 | Write endpoints had no authentication | Critical | Fixed | `TestDefect003Authorization` |
