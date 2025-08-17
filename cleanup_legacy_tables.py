import os
import shutil
import sqlite3
from datetime import datetime


def backup_database(db_path: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.bak_{timestamp}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def drop_legacy_tables(db_path: str, tables: list[str]) -> dict[str, str]:
    results: dict[str, str] = {}
    connection = sqlite3.connect(db_path)
    try:
        with connection:
            for table_name in tables:
                try:
                    connection.execute(f"DROP TABLE IF EXISTS {table_name}")
                    results[table_name] = "dropped_or_not_present"
                except Exception as exc:  # noqa: BLE001
                    results[table_name] = f"error: {exc}"
    finally:
        connection.close()
    return results


def main() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, "database", "db.sqlite3")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    print(f"Backing up database: {db_path}")
    backup_path = backup_database(db_path)
    print(f"Backup created at: {backup_path}")

    legacy_tables = [
        "scraper_spider",
        "jobs_job",
    ]
    print(f"Dropping legacy tables if they exist: {legacy_tables}")
    results = drop_legacy_tables(db_path, legacy_tables)
    for name, status in results.items():
        print(f" - {name}: {status}")

    print("Cleanup complete.")


if __name__ == "__main__":
    main()


