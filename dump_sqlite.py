import json
import os
import sqlite3
import sys


def dump_sqlite_database(database_path: str) -> dict:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    tables = [
        row[0]
        for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type in ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]

    data: dict[str, list[dict] | dict] = {}
    for table_name in tables:
        try:
            rows = [dict(row) for row in cursor.execute("SELECT * FROM " + table_name).fetchall()]
        except Exception as exc:  # noqa: BLE001
            rows = {"error": str(exc)}
        data[table_name] = rows

    return {"tables": tables, "data": data}


def main() -> None:
    default_db = os.path.join(
        os.getcwd(),
        "database",
        "db.sqlite3",
    )

    database_path = sys.argv[1] if len(sys.argv) > 1 else default_db
    result = dump_sqlite_database(database_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()


