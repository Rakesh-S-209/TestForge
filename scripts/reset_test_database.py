"""Delete all generated SQLite databases to reset the development environment.

Tests always use isolated in-memory databases and are unaffected by this script.
Only the developer-facing database (testforge.db) is removed.

Usage:
    python scripts/reset_test_database.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_FILES = [
    ROOT / "testforge.db",
    ROOT / "testforge_test.db",
]


def main() -> None:
    removed = 0
    for db in DB_FILES:
        if db.exists():
            db.unlink()
            print(f"Removed: {db}")
            removed += 1

    if removed == 0:
        print("No database files found — nothing to remove.")
    else:
        print(f"Reset complete ({removed} file(s) removed).")


if __name__ == "__main__":
    main()
