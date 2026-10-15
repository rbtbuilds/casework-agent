from pathlib import Path


def pytest_configure() -> None:
    (Path(__file__).resolve().parents[1] / ".runtime").mkdir(exist_ok=True)
