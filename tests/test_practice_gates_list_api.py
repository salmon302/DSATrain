from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_gates_list_get_delete(tmp_path, monkeypatch):
    # JSON fallback shouldn't be used here since we have DB; but ensure isolation for file fallback anyway
    from src.services import gated_practice as gp_mod
    monkeypatch.setattr(gp_mod, "DEFAULT_STORE", tmp_path / "practice_sessions.json", raising=False)

    # Start one session
    r1 = client.post("/practice/gates/start", json={"problem_id": "pX", "session_id": "sess_test"})
    assert r1.status_code == 200
    # Progress one gate
    r2 = client.post("/practice/gates/progress", json={"session_id": "sess_test", "gate": "dry_run", "value": True})
    assert r2.status_code == 200

    # List sessions
    rlist = client.get("/practice/gates")
    assert rlist.status_code == 200
    items = rlist.json()
    assert any(x["session_id"] == "sess_test" for x in items)

    # Get specific
    rget = client.get("/practice/gates/sess_test")
    assert rget.status_code == 200
    assert rget.json()["gates"]["dry_run"] is True

    # Delete
    rdel = client.delete("/practice/gates/sess_test")
    assert rdel.status_code == 200
    assert rdel.json()["deleted"] is True

    # Verify missing
    rget2 = client.get("/practice/gates/sess_test")
    assert rget2.status_code == 404
