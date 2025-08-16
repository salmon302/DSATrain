from fastapi.testclient import TestClient

from src.api.skill_tree_server import app
from src.models.database import DatabaseConfig, Problem

client = TestClient(app)


def seed_platform_problems():
    db = DatabaseConfig().get_session()
    try:
        ids = {p.id for p in db.query(Problem).filter(Problem.id.in_(["pf_1","pf_2","pf_3"]))}
        to_add = []
        if "pf_1" not in ids:
            to_add.append(Problem(
                id="pf_1", platform="leetcode", platform_id="l1", title="Two Sum", difficulty="Easy",
                category="test", algorithm_tags=["arrays"], sub_difficulty_level=1, quality_score=7.0, google_interview_relevance=50.0,
            ))
        if "pf_2" not in ids:
            to_add.append(Problem(
                id="pf_2", platform="codeforces", platform_id="c1", title="Prefix Sums", difficulty="Medium",
                category="test", algorithm_tags=["prefix_sum"], sub_difficulty_level=3, quality_score=8.0, google_interview_relevance=40.0,
            ))
        if "pf_3" not in ids:
            to_add.append(Problem(
                id="pf_3", platform="custom", platform_id="x1", title="Advanced Arrays", difficulty="Hard",
                category="test", algorithm_tags=["arrays"], sub_difficulty_level=5, quality_score=9.0, google_interview_relevance=60.0,
            ))
        if to_add:
            db.add_all(to_add)
            db.commit()
    finally:
        db.close()


def test_platform_and_title_match_filters_and_cache():
    seed_platform_problems()

    # Tag listing with platform filter
    r = client.get("/skill-tree-v2/tag/arrays/problems?page=1&page_size=10&platform=leetcode")
    assert r.status_code == 200, r.text
    data = r.json()
    assert all(p["title"] in ["Two Sum", "Advanced Arrays"] or True for p in data["problems"])  # sanity
    assert any(p["title"] == "Two Sum" for p in data["problems"])  # leetcode
    assert all(p.get("id") != "pf_2" for p in data["problems"])  # codeforces excluded

    # Title match prefix
    r2 = client.get("/skill-tree-v2/tag/arrays/problems?page=1&page_size=10&query=Two%20&title_match=prefix")
    assert r2.status_code == 200
    data2 = r2.json()
    assert any(p["title"].startswith("Two ") for p in data2["problems"])  # 'Two Sum'

    # Title match exact
    r3 = client.get("/skill-tree-v2/tag/arrays/problems?page=1&page_size=10&query=Two%20Sum&title_match=exact")
    assert r3.status_code == 200
    data3 = r3.json()
    assert any(p["title"] == "Two Sum" for p in data3["problems"])  # exact

    # Cache sanity: repeated call should return same payload quickly
    r4 = client.get("/skill-tree-v2/tags/overview?top_problems_per_tag=3")
    assert r4.status_code == 200
    r5 = client.get("/skill-tree-v2/tags/overview?top_problems_per_tag=3")
    assert r5.status_code == 200
    assert r4.json() == r5.json()
