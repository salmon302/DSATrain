from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_gated_practice_flow(tmp_path, monkeypatch):
    # Override store path to temporary file for test isolation
    from src.services import gated_practice as gp_mod
    monkeypatch.setattr(gp_mod, "DEFAULT_STORE", tmp_path / "practice_sessions.json", raising=False)

    # Start
    r1 = client.post("/practice/gates/start", json={"problem_id": "p1"})
    assert r1.status_code == 200, r1.text
    sess = r1.json()
    sid = sess["session_id"]

    # Progress gates
    r2 = client.post("/practice/gates/progress", json={"session_id": sid, "gate": "dry_run", "value": True})
    assert r2.status_code == 200, r2.text
    r3 = client.post("/practice/gates/progress", json={"session_id": sid, "gate": "pseudocode", "value": True})
    assert r3.status_code == 200, r3.text

    # Status should not be unlocked yet
    rstat = client.get("/practice/gates/status", params={"session_id": sid})
    assert rstat.status_code == 200
    assert rstat.json()["unlocked"] is False

    # Final gate unlocks
    r4 = client.post("/practice/gates/progress", json={"session_id": sid, "gate": "code", "value": True})
    assert r4.status_code == 200
    assert r4.json()["unlocked"] is True
