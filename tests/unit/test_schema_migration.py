import sqlite3
from pathlib import Path

import pytest

from casework_agent.repository import Repository


def test_future_schema_is_rejected_without_mutating_it(tmp_path: Path) -> None:
    path = tmp_path / "future.sqlite3"
    with sqlite3.connect(path) as con:
        con.execute(
            "CREATE TABLE schema_migrations(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL)"
        )
        con.execute("INSERT INTO schema_migrations VALUES(99,'future')")
    with pytest.raises(RuntimeError, match="unsupported_schema_version"), Repository.open(path):
        pass
    with sqlite3.connect(path) as con:
        assert con.execute("SELECT version FROM schema_migrations").fetchall() == [(99,)]
        assert con.execute("SELECT name FROM sqlite_master WHERE name='cases'").fetchone() is None
