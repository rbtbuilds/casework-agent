from pathlib import Path

from fastapi.testclient import TestClient

from casework_agent.api import create_app
from casework_agent.config import Settings


def test_body_size_and_missing_key_have_shared_errors(tmp_path: Path) -> None:
    with TestClient(create_app(Settings(root=tmp_path, run_worker=False))) as client:
        huge = client.post(
            "/v1/cases",
            content='"' + "x" * 33000 + '"',
            headers={"Content-Type": "application/json", "Idempotency-Key": "huge"},
        )
        assert huge.status_code == 413 and huge.json()["error"]["code"] == "request_too_large"
        missing = client.post("/v1/cases", json={})
        assert missing.status_code == 422 and missing.json()["error"]["code"] == "validation_error"
        absent = client.get("/v1/cases/missing")
        assert absent.status_code == 404 and absent.json()["error"]["code"] == "not_found"
