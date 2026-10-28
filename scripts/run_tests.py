r"""Convenience script: run the full test suite, generate all reports.

Usage (from repo root):
    # Windows PowerShell
    .\.venv\Scripts\python.exe scripts/run_tests.py

    # Linux / macOS / GitHub Actions
    .venv/bin/python scripts/run_tests.py

After completion, the following files are created / updated:
    reports/test_report.html        — pytest-html report
    reports/test_results.json       — pytest-json-report output
    reports/coverage.json           — pytest-cov JSON output
    reports/coverage_html/          — line-by-line coverage
    reports/summary.json            — dashboard-ready merged summary
"""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

PYTHON = sys.executable


def run_tests() -> int:
    """Execute pytest with all report flags.  Returns the exit code."""
    cmd = [
        PYTHON, "-m", "pytest",
        "tests/",
        "--tb=short",
        "-v",
        f"--html={REPORTS}/test_report.html",
        "--self-contained-html",
        "--cov=app",
        f"--cov-report=html:{REPORTS}/coverage_html",
        f"--cov-report=json:{REPORTS}/coverage.json",
        "--cov-report=term",
        "--json-report",
        f"--json-report-file={REPORTS}/test_results.json",
    ]
    print("Running test suite…")
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode


def generate_summary() -> None:
    """Call the report parser to produce summary.json."""
    # Import here so this script is usable even if top-level imports fail
    sys.path.insert(0, str(ROOT))
    from reporting.report_parser import generate_dashboard_summary

    timestamp = datetime.now(UTC).isoformat()
    data = generate_dashboard_summary(
        results_path=REPORTS / "test_results.json",
        coverage_path=REPORTS / "coverage.json",
        output_path=REPORTS / "summary.json",
        timestamp=timestamp,
    )
    print(f"\nDashboard summary: {REPORTS / 'summary.json'}")
    print(
        f"  {data.total} tests | {data.passed} passed"
        f" | {data.pass_rate}% | {data.coverage_total}% coverage"
    )


if __name__ == "__main__":
    code = run_tests()
    generate_summary()
    print("\nDone.  Open dashboard/index.html in a browser to view results.")
    sys.exit(code)
