from datetime import UTC, datetime
from pathlib import Path

import pytest

from casework_agent.clock import FrozenClock
from casework_agent.contracts import CaseSeed
from casework_agent.hashing import canonical_hash
from casework_agent.repository import Repository


def test_reopen_preserves_case(tmp_path: Path) -> None:
    clock = FrozenClock(datetime(2026, 10, 15, tzinfo=UTC))
    path = tmp_path / "app.sqlite3"
    seed = CaseSeed(scenario_id="dev-delay-01", order_id="o-001", as_of=clock.now(), mode="fixture")
    with Repository.open(path, clock) as repo:
        case = repo.create_case(seed)
    with Repository.open(path, clock) as repo:
        assert repo.get_case(case.id).state == "new"
        assert repo.get_case(case.id).version == 1


def test_canonical_hash_is_stable() -> None:
    assert canonical_hash({"b": 2, "a": 1}) == canonical_hash({"a": 1, "b": 2})
    with pytest.raises(ValueError):
        canonical_hash({"a": float("nan")})
