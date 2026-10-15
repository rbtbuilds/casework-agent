import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Self

from .clock import Clock, SystemClock
from .contracts import CaseSeed, CaseView, uid
from .db import connect


class Repository:
    def __init__(self, path: Path, clock: Clock | None = None) -> None:
        self.path = path
        self.clock = clock or SystemClock()
        self.con = connect(path)
    @classmethod
    def open(cls, path: Path, clock: Clock | None = None) -> Self:
        return cls(path, clock)
    def __enter__(self) -> Self:
        return self
    def __exit__(self, *args: object) -> None:
        self.close()
    def close(self) -> None:
        self.con.close()
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        self.con.execute("BEGIN IMMEDIATE")
        try:
            yield self.con
            self.con.execute("COMMIT")
        except BaseException:
            self.con.execute("ROLLBACK")
            raise
    def create_case(self, seed: CaseSeed) -> CaseView:
        id = uid()
        now = self.clock.now().isoformat()
        with self.transaction():
            self.con.execute("INSERT INTO cases(id,seed_json,state,version,created_at,updated_at) VALUES(?,?,'new',1,?,?)", (id,seed.model_dump_json(),now,now))
        return self.get_case(id)
    def get_case(self, id: str) -> CaseView:
        row = self.con.execute("SELECT * FROM cases WHERE id=?",(id,)).fetchone()
        if row is None:
            raise KeyError(id)
        seed = CaseSeed.model_validate_json(str(row["seed_json"]))
        return CaseView(id=id,**seed.model_dump(),state=row["state"],version=row["version"])
