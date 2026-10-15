import sqlite3
from pathlib import Path


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, isolation_level=None, timeout=5)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=5000")
        exists = con.execute(
            "SELECT name FROM sqlite_master WHERE name='schema_migrations'"
        ).fetchone()
        version = (
            con.execute("SELECT COALESCE(MAX(version),0) FROM schema_migrations").fetchone()[0]
            if exists
            else 0
        )
        if version not in {0, 1, 2}:
            raise RuntimeError("unsupported_schema_version")
        if version < 2:
            scripts: list[str] = []
            for next_version in range(version + 1, 3):
                name = "001_initial.sql" if next_version == 1 else "002_gathering_runs.sql"
                scripts.append((Path(__file__).parent / "migrations" / name).read_text())
                scripts.append(
                    f"INSERT OR IGNORE INTO schema_migrations VALUES({next_version},datetime('now'));"
                )
            con.executescript("BEGIN IMMEDIATE;\n" + "\n".join(scripts) + "\nCOMMIT;")
        return con
    except BaseException:
        if con.in_transaction:
            con.rollback()
        con.close()
        raise
