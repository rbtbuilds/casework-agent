from fastapi import FastAPI

from .config import Settings
from .repository import Repository


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    app = FastAPI(title="Casework Agent", version="0.1.0")
    @app.get("/health")
    def health() -> dict[str, object]:
        with Repository.open(config.database) as repo:
            version = repo.con.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
        return {"status": "ok", "schema_version": version, "model_available": False, "fixture_available": True}
    return app
