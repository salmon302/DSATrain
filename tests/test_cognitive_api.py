from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

def test_cognitive_profile_and_adaptation():
    # Get default profile (should auto-create)
    resp = client.get("/cognitive/profile", params={"user_id": "default_user"})
    assert resp.status_code == 200, resp.text
    prof = resp.json()
    assert prof["user_id"] == "default_user"

    # Assess and update
    resp2 = client.post(
        "/cognitive/assess",
        json={
            "user_id": "default_user",
            "working_memory_quiz": 8,
            "style_preference": "visual",
            "visual_vs_verbal": 0.8,
            "processing_speed_hint": "average",
        },
    )
    assert resp2.status_code == 200, resp2.text
    prof2 = resp2.json()
    assert prof2["working_memory_capacity"] == 8
    assert prof2["learning_style_preference"] == "visual"

    # Get adaptation
    resp3 = client.get("/cognitive/adaptation", params={"user_id": "default_user"})
    assert resp3.status_code == 200, resp3.text
    adapt = resp3.json()
    assert "recommendations" in adapt and isinstance(adapt["recommendations"], list)
