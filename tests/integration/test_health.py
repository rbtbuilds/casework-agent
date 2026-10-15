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


def test_model_readiness_requires_this_snapshot_and_protocol(tmp_path: Path) -> None:
    import json

    from casework_agent.contracts import JsonDict
    from casework_agent.hashing import canonical_hash
    from casework_agent.model_adapter import MODEL_PROTOCOL_VERSION

    models = tmp_path / ".runtime/models"
    models.mkdir(parents=True)
    identity: JsonDict = {"model_id": "synthetic/model", "revision": "synthetic", "files": {}}
    (models / "snapshot.json").write_text(json.dumps({**identity, "path": str(models)}))
    probe = tmp_path / ".runtime/model-probe.json"
    result = {
        "protocol_valid": True,
        "protocol_version": MODEL_PROTOCOL_VERSION,
        "snapshot_hash": canonical_hash(identity),
    }
    probe.write_text(json.dumps(result))
    with TestClient(create_app(Settings(root=tmp_path, run_worker=False))) as client:
        assert client.get("/health").json()["model_available"] is True
        probe.write_text(json.dumps({**result, "snapshot_hash": "other-model"}))
        assert client.get("/health").json()["model_available"] is False
        probe.write_text(json.dumps({**result, "protocol_version": "obsolete-protocol"}))
        assert client.get("/health").json()["model_available"] is False
        probe.write_text("{broken")
        assert client.get("/health").json()["model_available"] is False
