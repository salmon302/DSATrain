from fastapi.testclient import TestClient

import src.api.main as main


def test_problems_list_shape():
    client = TestClient(main.app)
    r = client.get("/problems", params={"limit": 5})
    assert r.status_code == 200
    data = r.json()
    assert "problems" in data and isinstance(data["problems"], list)
    assert "count" in data and "total_available" in data
    assert "filters_applied" in data


def test_problem_not_found_and_solutions_not_found():
    client = TestClient(main.app)
    # Force a non-existent ID
    r1 = client.get("/problems/does-not-exist")
    assert r1.status_code == 404

    r2 = client.get("/problems/does-not-exist/solutions")
    assert r2.status_code == 404


def test_analytics_shapes():
    client = TestClient(main.app)

    # platform analytics
    r1 = client.get("/analytics/platforms")
    assert r1.status_code == 200
    d1 = r1.json()
    assert "platform_analytics" in d1

    # difficulty analytics
    r2 = client.get("/analytics/difficulty")
    assert r2.status_code == 200
    d2 = r2.json()
    assert "difficulty_analytics" in d2

    # algorithm tag analytics
    r3 = client.get("/analytics/algorithm-tags")
    assert r3.status_code == 200
    d3 = r3.json()
    assert "algorithm_tag_analytics" in d3
