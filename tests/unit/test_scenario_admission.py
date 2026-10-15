from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from casework_agent.api import create_app
from casework_agent.config import Settings


@pytest.mark.parametrize(
    "field,value",
    [("scenario_id", "unregistered"), ("order_id", "o-other"), ("as_of", "2099-01-01T00:00:00Z")],
)
def test_create_requires_admitted_scenario_tuple(tmp_path: Path, field: str, value: str) -> None:
    with TestClient(create_app(Settings(root=tmp_path, run_worker=False))) as client:
        seed = {
            "scenario_id": "dev-delay-01",
            "order_id": "o-001",
            "as_of": "2026-10-15T12:00:00Z",
            "mode": "fixture",
        }
        seed[field] = value
        response = client.post("/v1/cases", json=seed, headers={"Idempotency-Key": "invalid-tuple"})
        assert response.status_code == 422
        assert client.get("/v1/cases").json() == []
