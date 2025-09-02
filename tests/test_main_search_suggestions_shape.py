from fastapi.testclient import TestClient

import src.api.main as main


def test_search_suggestions_shape():
    client = TestClient(main.app)
    r = client.get("/search/suggestions", params={"partial": "bin"})
    assert r.status_code == 200
    data = r.json()
    assert "suggestions" in data and isinstance(data["suggestions"], list)
    # Should not exceed the limit enforced by the endpoint (10)
    assert len(data["suggestions"]) <= 10
    assert data.get("query") == "bin"
