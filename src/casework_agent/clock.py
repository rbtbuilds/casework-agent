from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass
class FrozenClock:
    value: datetime

    def now(self) -> datetime:
        return self.value


@dataclass
class FileClock:
    """Explicit test-fixture clock, read afresh so expiry can be exercised without sleeping."""

    path: Path

    def now(self) -> datetime:
        value = datetime.fromisoformat(self.path.read_text().strip())
        if value.tzinfo is None:
            raise ValueError("Fixture clock requires timezone")
        return value.astimezone(UTC)
