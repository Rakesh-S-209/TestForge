# TestForge — API Testing & Automation Framework

A complete, portfolio-quality SDET project demonstrating REST API development, test design, automated test execution, coverage measurement, defect investigation, regression testing, and CI/CD — built with **FastAPI**, **pytest**, and **GitHub Actions**.

---

## What This Project Demonstrates

| Skill | Evidence |
|---|---|
| REST API design | FastAPI Store API with CRUD, auth, orders |
| Unit testing | 45 unit tests for schemas, services, JWT helpers |
| API integration testing | 63 integration tests with isolated in-memory DB |
| Negative / boundary testing | Zero price, page_size=0, oversized inputs, wrong types |
| Regression testing | 7 regression tests, one per documented defect |
| Security-oriented testing | Auth enforcement, injection handling, safe errors |
| Code coverage | 85% measured via pytest-cov |
| HTML + JSON reporting | pytest-html, pytest-json-report, custom dashboard |
| CI/CD | GitHub Actions on push + PR |
| Defect documentation | 3 defects with root cause, reproduction, and fix |
| Test case catalogue | 130 cases with IDs, severity, and actual results |

---

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.13 |
| API framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via aiosqlite |
| Test framework | pytest 8.3 + pytest-asyncio |
| HTTP testing | HTTPX AsyncClient |
| Coverage | pytest-cov |
| Reporting | pytest-html, pytest-json-report |
| Linting | Ruff |
| Auth | bcrypt + python-jose JWT |
| CI | GitHub Actions |
| Dashboard | Vanilla HTML/CSS/JS |

---

## Project Structure

```
testforge/
├── app/                        # Application under test
│   ├── api/v1/                 #   Routers: products, auth, orders
│   ├── models/                 #   SQLAlchemy ORM models
│   ├── schemas/                #   Pydantic request/response schemas
│   ├── services/               #   Business logic layer
│   ├── repositories/           #   Database access layer
│   ├── config.py               #   Settings (pydantic-settings)
│   ├── database.py             #   Async engine + session factory
│   └── main.py                 #   FastAPI app factory
├── tests/
│   ├── unit/                   #   Schema + service unit tests
│   ├── integration/            #   Full HTTP endpoint tests
│   ├── regression/             #   One test per confirmed defect
│   ├── security/               #   Auth, injection, error safety
│   └── conftest.py             #   Shared fixtures (isolated DB)
├── test_cases/
│   └── test_case_catalogue.md  #   130 test cases with results
├── reporting/
│   ├── report_parser.py        #   Parses pytest output → summary.json
│   └── generate_report.py      #   CLI: generate dashboard data
├── dashboard/
│   ├── index.html              #   Live dashboard
│   ├── styles.css
│   └── app.js
├── scripts/
│   ├── run_tests.py            #   One-command: test + report
│   └── reset_test_database.py  #   Delete dev databases
├── docs/
│   ├── architecture.md
│   ├── test_strategy.md
│   ├── test_plan.md
│   └── defect_log.md
├── .github/workflows/tests.yml #   CI pipeline
├── reports/                    #   Generated (git-ignored)
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Clone and create a virtual environment

```powershell
# Windows PowerShell
git clone <repo-url>
cd TestForge
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
git clone <repo-url>
cd TestForge
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
# or with editable install:
pip install -e ".[dev]" && pip install "pydantic[email]" greenlet pytest-json-report
```

### 3. Start the API

```powershell
# Windows
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

```bash
# Linux / macOS
python -m uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

---

## Running the Tests

### All tests (quick)

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

### All tests + all reports (recommended)

```powershell
.\.venv\Scripts\python.exe scripts/run_tests.py
```

This generates:
- `reports/test_report.html` — human-readable HTML report
- `reports/test_results.json` — machine-readable JSON
- `reports/coverage.json` — coverage data
- `reports/coverage_html/` — line-by-line coverage browser
- `reports/summary.json` — dashboard data

### Individual categories

```powershell
# Unit tests only
.\.venv\Scripts\python.exe -m pytest tests/unit/ -v

# Integration tests only
.\.venv\Scripts\python.exe -m pytest tests/integration/ -v

# Regression tests only
.\.venv\Scripts\python.exe -m pytest tests/regression/ -v

# Security tests only
.\.venv\Scripts\python.exe -m pytest tests/security/ -v
```

### Linting

```powershell
.\.venv\Scripts\python.exe -m ruff check app/ tests/ reporting/ scripts/
```

---

## Viewing Reports

### Dashboard
Open `dashboard/index.html` in a browser (or serve with any static file server).

The dashboard reads `reports/summary.json` automatically. Run `scripts/run_tests.py` first to populate it.

```powershell
# Serve locally (Python built-in)
.\.venv\Scripts\python.exe -m http.server 8080
# Then open http://localhost:8080/dashboard/
```

### HTML Test Report
Open `reports/test_report.html` directly in a browser.

### Coverage Report
Open `reports/coverage_html/index.html` in a browser.

---

## API Endpoints

| Method | URL | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Health status |
| GET | `/api/v1/products` | No | List products (paginated) |
| GET | `/api/v1/products/{id}` | No | Get one product |
| POST | `/api/v1/products` | Yes | Create a product |
| PUT | `/api/v1/products/{id}` | Yes | Update a product |
| DELETE | `/api/v1/products/{id}` | Yes | Delete a product |
| POST | `/api/v1/auth/register` | No | Register demo user |
| POST | `/api/v1/auth/login` | No | Login → JWT token |
| GET | `/api/v1/orders` | Yes | List own orders |
| POST | `/api/v1/orders` | Yes | Place an order |

### Sample Requests

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"demo1234"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}'
# → {"access_token": "<jwt>", "token_type": "bearer"}

# Create product (use the token from login)
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget Pro","price":29.99,"stock":100,"category":"widgets"}'

# List products
curl http://localhost:8000/api/v1/products?page=1&page_size=10
```

---

## Understanding Coverage

The 85% coverage figure means 85% of the **statements** in `app/` were executed by at least one test.

| What 85% means | What it does NOT mean |
|---|---|
| Most application paths were executed | Every possible combination was tested |
| The main happy paths and error paths work | The application is production-ready |
| Untested code is identified | Untested code is necessarily broken |

The remaining 15% consists mainly of error-handling branches in repositories and auth service paths (e.g., the `except` clause in `verify_password`).

---

## Business Rules

| Rule | Enforcement |
|---|---|
| Product name must be non-empty and non-blank | Pydantic validator + service layer |
| Price must be > 0 | Pydantic Field `gt=0` |
| Stock must be ≥ 0 | Pydantic Field `ge=0` |
| Product names are unique | Service layer duplicate check |
| page must be ≥ 1 | FastAPI Query constraint + service |
| page_size must be in [1, 100] | FastAPI Query constraint + service |
| Write operations require a valid JWT | `Depends(get_current_user)` on all mutating routes |
| Orders may not exceed available stock | Orders service stock check |
| Users may only see their own orders | Repository filters by `user_id` |

---

## GitHub Actions

The workflow at `.github/workflows/tests.yml` runs on every push and pull request to `main` or `develop`.

Steps:
1. Checkout code
2. Set up Python (3.12 and 3.13 matrix)
3. Install dependencies
4. Run Ruff linting
5. Execute all 130 tests with coverage
6. Generate `summary.json`
7. Upload reports as CI artefacts (retained 30 days)

The workflow fails if any test fails or if Ruff reports errors.

> **Note:** A GitHub Actions run cannot be confirmed as passing until the repository is pushed to GitHub and the Actions tab shows a completed run. The workflow file is correctly configured; status must be verified from the GitHub UI.

---

## Controlled Defect Exercises

Three representative defects are documented in `docs/defect_log.md`:

| ID | Defect | Test |
|---|---|---|
| DEFECT-001 | Zero price accepted | `TestDefect001PriceValidation` |
| DEFECT-002 | `page_size=0` caused HTTP 500 | `TestDefect002PaginationBoundary` |
| DEFECT-003 | Unauthenticated write access | `TestDefect003Authorization` |

All three defects are **fixed in the default codebase**. The regression tests pass, and would fail if the defects were reintroduced.

---

## Known Limitations

- SQLite is not suitable for production or concurrent high-write workloads
- The JWT secret key is a demo value — replace before any real deployment
- No token refresh or revocation mechanism
- `python-jose` emits a deprecation warning about `datetime.utcnow()`; this is a third-party library issue
- Coverage does not include `tests/` themselves (tests are not application code)
- No real email delivery or payment processing

---

## Future Improvements

- Add PostgreSQL support and a Docker Compose setup
- Implement token refresh and logout (blacklist)
- Add role-based access control (admin vs. customer)
- Add parametrized test cases for more boundary combinations
- Integrate mypy strict mode
- Add contract tests validating the OpenAPI schema against live responses
- Add a Locust performance test scenario

---

## License

MIT — see `LICENSE`.
