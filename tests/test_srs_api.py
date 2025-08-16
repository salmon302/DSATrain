from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.main import app
from src.models.database import DatabaseConfig, Problem, ReviewCard

client = TestClient(app)

def seed_problem():
    db = DatabaseConfig().get_session()
    try:
        p = db.query(Problem).filter(Problem.id == "srs_test_1").first()
        if not p:
            p = Problem(
                id="srs_test_1",
                platform="custom",
                platform_id="p1",
                title="SRS Test Problem",
                difficulty="Easy",
                category="test",
                algorithm_tags=["arrays"],
                google_interview_relevance=10.0,
                quality_score=10.0,
            )
            db.add(p)
            db.commit()
    finally:
        db.close()


def test_srs_flow_basic():
    seed_problem()

    # Initial stats
    resp_stats = client.get("/srs/stats")
    assert resp_stats.status_code == 200
    stats0 = resp_stats.json()

    # Next cards should be zero initially
    resp_next = client.get("/srs/next")
    assert resp_next.status_code == 200
    data_next = resp_next.json()
    assert data_next["count"] >= 0

    # Submit a review to create a card
    resp_review = client.post("/srs/review", json={"problem_id": "srs_test_1", "outcome": "good"})
    assert resp_review.status_code == 200, resp_review.text
    review_data = resp_review.json()
    assert review_data["problem_id"] == "srs_test_1"
    assert review_data["interval_days"] >= 1

    # Stats should reflect cards/reviews
    resp_stats2 = client.get("/srs/stats")
    assert resp_stats2.status_code == 200
    stats1 = resp_stats2.json()
    assert stats1["total_cards"] >= stats0.get("total_cards", 0)
    assert stats1["total_reviews"] >= stats0.get("total_reviews", 0)

    # Force the card to be due and fetch next
    db = DatabaseConfig().get_session()
    try:
        card = db.query(ReviewCard).filter(ReviewCard.problem_id == "srs_test_1").first()
        assert card is not None
        card.next_review_at = datetime.now() - timedelta(days=1)
        db.commit()
    finally:
        db.close()

    resp_next2 = client.get("/srs/next")
    assert resp_next2.status_code == 200
    data_next2 = resp_next2.json()
    assert data_next2["count"] >= 1

    # Log retrieval practice
    resp_retrieval = client.post(
        "/srs/retrieval-practice",
        json={
            "problem_id": "srs_test_1",
            "retrieval_type": "micro",
            "success_rate": 0.8,
            "retrieval_strength": 0.6,
        },
    )
    assert resp_retrieval.status_code == 200, resp_retrieval.text
