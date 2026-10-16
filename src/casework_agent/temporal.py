from datetime import UTC, datetime, timedelta


def to_utc(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is None:
        return None
    try:
        return value.astimezone(UTC)
    except OverflowError as exc:
        raise ValueError("timestamp_out_of_utc_range") from exc


def elapsed_microseconds(later: datetime | None, earlier: datetime | None) -> int | None:
    end, start = to_utc(later), to_utc(earlier)
    if end is None or start is None:
        return None
    return (end - start) // timedelta(microseconds=1)
