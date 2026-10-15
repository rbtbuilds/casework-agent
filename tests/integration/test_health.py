from pathlib import Path

from fastapi.testclient import TestClient

from casework_agent.api import create_app
from casework_agent.config import Settings


def test_health_without_model(tmp_path: Path) -> None:
    with TestClient(create_app(Settings(root=tmp_path))) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["model_available"] is False
