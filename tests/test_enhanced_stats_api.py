from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_enhanced_stats_smoke():
    # Overview
    r1 = client.get("/enhanced-stats/overview")
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert "overview" in data1 and isinstance(data1["overview"], dict)
    assert "total_problems" in data1["overview"]

    # Algorithm relevance
    r2 = client.get("/enhanced-stats/algorithm-relevance")
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert "algorithm_analysis" in data2 and isinstance(data2["algorithm_analysis"], list)

    # Difficulty calibration
    r3 = client.get("/enhanced-stats/difficulty-calibration")
    assert r3.status_code == 200, r3.text
    data3 = r3.json()
    assert "calibration_analysis" in data3 and isinstance(data3["calibration_analysis"], list)

    # Interview readiness
    r4 = client.get("/enhanced-stats/interview-readiness")
    assert r4.status_code == 200, r4.text
    data4 = r4.json()
    assert "overview" in data4 and "readiness_score" in data4["overview"]

    # Quality improvements
    r5 = client.get("/enhanced-stats/quality-improvements")
    assert r5.status_code == 200, r5.text
    data5 = r5.json()
    assert "improvements" in data5 and "current_distribution" in data5
