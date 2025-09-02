from fastapi.testclient import TestClient

import src.api.main as main


class StubBehaviorTracker:
    def __init__(self):
        self.calls = []

    def track_problem_view(self, **kwargs):
        self.calls.append(("viewed", kwargs))

    def track_problem_attempt(self, **kwargs):
        self.calls.append(("attempted", kwargs))

    def track_bookmark_action(self, **kwargs):
        self.calls.append(("bookmarked", kwargs))


def test_interactions_viewed_and_attempted(monkeypatch):
    tracker = StubBehaviorTracker()

    # Override dependency to use our stub tracker
    main.app.dependency_overrides[main.get_behavior_tracker] = lambda: tracker

    client = TestClient(main.app)

    r1 = client.post(
        "/interactions/track",
        params={
            "user_id": "u1",
            "problem_id": "p1",
            "action": "viewed",
            "time_spent": 12,
            "session_id": "s1",
            "metadata": "{}",
        },
    )
    assert r1.status_code == 200
    assert r1.json().get("status") == "success"

    r2 = client.post(
        "/interactions/track",
        params={
            "user_id": "u2",
            "problem_id": "p2",
            "action": "attempted",
            "success": True,
            "time_spent": 30,
            "session_id": "s2",
        },
    )
    assert r2.status_code == 200
    assert r2.json().get("status") == "success"

    # Ensure our stub recorded calls
    kinds = [k for (k, _payload) in tracker.calls]
    assert "viewed" in kinds and "attempted" in kinds

    # Clean up overrides to avoid side effects on other tests
    main.app.dependency_overrides.pop(main.get_behavior_tracker, None)
