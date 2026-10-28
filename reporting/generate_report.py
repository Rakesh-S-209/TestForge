"""CLI entry-point for generating the dashboard summary file.

Usage:
    python reporting/generate_report.py

Reads:
    reports/test_results.json  — pytest-json-report output
    reports/coverage.json      — pytest-cov JSON output

Writes:
    reports/summary.json       — merged dashboard-ready data

Run the tests first with the run_tests.py script so these inputs exist.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

# Allow running directly without installing the package
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from reporting.report_parser import generate_dashboard_summary  # noqa: E402


def main() -> None:
    reports_dir = ROOT / "reports"
    results_path = reports_dir / "test_results.json"
    coverage_path = reports_dir / "coverage.json"
    output_path = reports_dir / "summary.json"

    if not results_path.exists():
        print(f"ERROR: {results_path} not found.  Run tests first with scripts/run_tests.py")
        sys.exit(1)

    timestamp = datetime.now(UTC).isoformat()
    data = generate_dashboard_summary(
        results_path=results_path,
        coverage_path=coverage_path,
        output_path=output_path,
        timestamp=timestamp,
    )

    print(f"Dashboard summary written to: {output_path}")
    print(f"  Total tests : {data.total}")
    print(f"  Passed      : {data.passed}")
    print(f"  Failed      : {data.failed}")
    print(f"  Pass rate   : {data.pass_rate}%")
    print(f"  Coverage    : {data.coverage_total}%")


if __name__ == "__main__":
    main()
