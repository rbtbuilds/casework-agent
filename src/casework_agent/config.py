from pathlib import Path

from pydantic import BaseModel, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    root: Path = Path.cwd()
    model_root: Path | None = None

    @property
    def model_directory(self) -> Path:
        return self.model_root or self.root

    orders_url: str = "http://127.0.0.1:8212"
    carrier_url: str = "http://127.0.0.1:8312"
    tickets_url: str = "http://127.0.0.1:8412"
    web_origin: str = "http://127.0.0.1:5112"
    run_worker: bool = True

    @property
    def runtime(self) -> Path:
        return self.root / ".runtime"

    @property
    def database(self) -> Path:
        return self.runtime / "app.sqlite3"
