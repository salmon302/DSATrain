from fastapi.testclient import TestClient

from src.api.skill_tree_server import app
from src.models.database import DatabaseConfig, Problem

client = TestClient(app)


def seed_tagged_problems():
    db = DatabaseConfig().get_session()
    try:
        existing = db.query(Problem).filter(Problem.id.in_(["tags_test_1", "tags_test_2", "tags_test_3"]))
        existing_ids = {p.id for p in existing}
        to_add = []
        if "tags_test_1" not in existing_ids:
            to_add.append(Problem(
                id="tags_test_1",
                platform="custom",
                platform_id="p1",
                title="Two Pointers Practice",
                difficulty="Easy",
                category="test",
                algorithm_tags=["two_pointers", "arrays"],
                sub_difficulty_level=2,
                quality_score=8.5,
                google_interview_relevance=20.0,
            ))
        if "tags_test_2" not in existing_ids:
            to_add.append(Problem(
                id="tags_test_2",
                platform="custom",
                platform_id="p2",
                title="Binary Search Basics",
                difficulty="Medium",
                category="test",
                algorithm_tags=["binary_search", "arrays"],
                sub_difficulty_level=3,
                quality_score=9.0,
                google_interview_relevance=30.0,
            ))
        if "tags_test_3" not in existing_ids:
            to_add.append(Problem(
                id="tags_test_3",
                platform="custom",
                platform_id="p3",
                title="Advanced Two Pointers",
                difficulty="Hard",
                category="test",
                algorithm_tags=["two_pointers"],
                sub_difficulty_level=5,
                quality_score=9.5,
                google_interview_relevance=40.0,
            ))
        if to_add:
            db.add_all(to_add)
            db.commit()
    finally:
        db.close()


def test_tags_overview_and_tag_listing():
    seed_tagged_problems()

    # Tags overview should contain our tags
    r = client.get("/skill-tree-v2/tags/overview?top_problems_per_tag=3")
    assert r.status_code == 200, r.text
    data = r.json()
    tags = {t["tag"]: t for t in data.get("tags", [])}
    assert "two_pointers" in tags
    assert "binary_search" in tags

    # List by specific tag
    r2 = client.get("/skill-tree-v2/tag/two_pointers/problems?page=1&page_size=10&sort_by=difficulty")
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    assert data2["total_count"] >= 2
    assert len(data2["problems"]) >= 1

    # Filter by difficulty
    r3 = client.get("/skill-tree-v2/tag/two_pointers/problems?page=1&page_size=10&difficulty=Hard")
    assert r3.status_code == 200, r3.text
    data3 = r3.json()
    assert any(p["difficulty"] == "Hard" for p in data3["problems"])

    # Query filter should narrow results by title/tag substring
    r4 = client.get("/skill-tree-v2/tag/two_pointers/problems?page=1&page_size=10&query=advanced")
    assert r4.status_code == 200
    data4 = r4.json()
    # Expect at least one match for the 'Advanced Two Pointers' seeded problem
    assert any("advanced" in p["title"].lower() for p in data4["problems"]) 
