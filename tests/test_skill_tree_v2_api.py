import os
import pathlib
from typing import List

from fastapi.testclient import TestClient


def _set_test_db_env(tmp_db_path: str):
    os.environ["DSATRAIN_DATABASE_URL"] = f"sqlite:///{tmp_db_path}"
    # Ensure tables auto-create for non-memory DBs
    os.environ["DSATRAIN_AUTO_CREATE_TABLES"] = "1"


def _seed_problems(db_session, problems: List[dict]):
    from src.models.database import Problem
    for p in problems:
        db_session.add(
            Problem(
                id=p["id"],
                platform=p.get("platform", "leetcode"),
                platform_id=p.get("platform_id", p["id"]),
                title=p.get("title", p["id"]).replace("_", " "),
                difficulty=p.get("difficulty", "Easy"),
                category=p.get("category"),
                description=p.get("description"),
                constraints=p.get("constraints"),
                examples=p.get("examples"),
                hints=p.get("hints"),
                algorithm_tags=p.get("algorithm_tags", []),
                data_structures=p.get("data_structures"),
                complexity_class=p.get("complexity_class"),
                google_interview_relevance=p.get("google_interview_relevance", 0.0),
                difficulty_rating=p.get("difficulty_rating", 0.0),
                quality_score=p.get("quality_score", 0.0),
                popularity_score=p.get("popularity_score", 0.0),
                pattern_tags=p.get("pattern_tags"),
                skill_areas=p.get("skill_areas"),
                granular_difficulty=p.get("granular_difficulty"),
                interview_frequency=p.get("interview_frequency"),
                company_tags=p.get("company_tags"),
                source_dataset=p.get("source_dataset"),
                canonical_solutions=p.get("canonical_solutions"),
                visual_aids=p.get("visual_aids"),
                verbal_explanations=p.get("verbal_explanations"),
                prerequisite_assessment=p.get("prerequisite_assessment"),
                elaborative_prompts=p.get("elaborative_prompts"),
                working_memory_load=p.get("working_memory_load"),
                sub_difficulty_level=p.get("sub_difficulty_level", 1),
                conceptual_difficulty=p.get("conceptual_difficulty", 50),
                implementation_complexity=p.get("implementation_complexity", 50),
                prerequisite_skills=p.get("prerequisite_skills", []),
                skill_tree_position=p.get("skill_tree_position", {}),
                primary_skill_area=p.get("primary_skill_area"),
                acceptance_rate=p.get("acceptance_rate"),
                frequency_score=p.get("frequency_score"),
                companies=p.get("companies"),
            )
        )
    db_session.commit()


def _init_app_and_db(tmp_db_path: str):
    _set_test_db_env(tmp_db_path)
    # Import after env vars so DatabaseConfig picks up test DB
    from src.models.database import DatabaseConfig

    # Evict modules to avoid reusing module-level DB engines between tests.
    import sys
    for mod in [
        "src.api.skill_tree_api_optimized",
        "src.api.skill_tree_api",
        "src.api.main",
    ]:
        sys.modules.pop(mod, None)

    # Fresh imports ensure module-level configs bind to the new DSATRAIN_DATABASE_URL
    import src.api.skill_tree_api_optimized as v2  # type: ignore
    import src.api.main as app_module  # type: ignore

    # Clear v2 in-process cache to avoid cross-test contamination
    if hasattr(v2, "_CACHE"):
        v2._CACHE.clear()

    # Ensure a clean schema
    dbc = DatabaseConfig(os.environ["DSATRAIN_DATABASE_URL"])
    try:
        dbc.drop_tables()
    except Exception:
        pass
    dbc.create_tables()

    client = TestClient(app_module.app)
    return client, dbc


def test_v2_skill_area_pagination_and_sorting(tmp_path):
    db_file = tmp_path / "v2_test.db"
    client, dbc = _init_app_and_db(str(db_file))

    # Seed 5 arrays and 3 graphs
    with dbc.get_session() as s:
        _seed_problems(
            s,
            [
                {"id": f"arr_{i}", "platform_id": f"arr_{i}", "difficulty": "Easy" if i < 2 else "Medium", "algorithm_tags": ["arrays", "two_pointers"], "quality_score": 5 + i, "google_interview_relevance": 10 + i, "sub_difficulty_level": 1, "primary_skill_area": "arrays"}
                for i in range(5)
            ]
            + [
                {"id": f"graph_{i}", "platform_id": f"graph_{i}", "difficulty": "Medium", "algorithm_tags": ["graphs", "bfs"], "quality_score": 6 + i, "google_interview_relevance": 5 + i, "sub_difficulty_level": 2, "primary_skill_area": "graphs"}
                for i in range(3)
            ],
        )

    # Page 1 of arrays, size 3, sort by quality desc
    resp = client.get(
        "/skill-tree-v2/skill-area/arrays/problems",
        params={"page": 1, "page_size": 3, "sort_by": "quality", "sort_order": "desc"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] == 5
    assert len(data["problems"]) == 3
    scores = [p["quality_score"] for p in data["problems"]]
    assert scores == sorted(scores, reverse=True)

    # Page 2
    resp2 = client.get(
        "/skill-tree-v2/skill-area/arrays/problems",
        params={"page": 2, "page_size": 3, "sort_by": "quality", "sort_order": "desc"},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["problems"]) == 2
    assert data2["has_next"] is False


def test_v2_skill_area_fallback_when_primary_null(tmp_path):
    db_file = tmp_path / "v2_test_null.db"
    client, dbc = _init_app_and_db(str(db_file))

    # Seed: one arrays with primary set, one arrays with primary null but tags indicate arrays
    with dbc.get_session() as s:
        _seed_problems(
            s,
            [
                {"id": "arr_primary", "platform_id": "arr_primary", "difficulty": "Easy", "algorithm_tags": ["arrays"], "quality_score": 9, "google_interview_relevance": 9, "sub_difficulty_level": 1, "primary_skill_area": "arrays"},
                {"id": "arr_null", "platform_id": "arr_null", "difficulty": "Easy", "algorithm_tags": ["arrays", "prefix_sum"], "quality_score": 7, "google_interview_relevance": 7, "sub_difficulty_level": 1, "primary_skill_area": None},
                {"id": "tree_other", "platform_id": "tree_other", "difficulty": "Easy", "algorithm_tags": ["trees"], "quality_score": 8, "google_interview_relevance": 8, "sub_difficulty_level": 1, "primary_skill_area": None},
            ],
        )

    resp = client.get(
        "/skill-tree-v2/skill-area/arrays/problems",
        params={"page": 1, "page_size": 10, "sort_by": "title", "sort_order": "asc"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Expect both arr_primary and arr_null included for arrays
    ids = [p["id"] for p in data["problems"]]
    assert set(["arr_primary", "arr_null"]).issubset(set(ids))
    # Ensure tree_other is excluded
    assert "tree_other" not in ids


def test_v2_tags_overview_counts(tmp_path):
    db_file = tmp_path / "v2_test_tags.db"
    client, dbc = _init_app_and_db(str(db_file))

    with dbc.get_session() as s:
        _seed_problems(
            s,
            [
                {"id": "p1", "platform_id": "p1", "difficulty": "Easy", "algorithm_tags": ["arrays", "two_pointers"], "quality_score": 6, "google_interview_relevance": 7, "sub_difficulty_level": 1},
                {"id": "p2", "platform_id": "p2", "difficulty": "Medium", "algorithm_tags": ["arrays", "sliding_window"], "quality_score": 7, "google_interview_relevance": 6, "sub_difficulty_level": 2},
                {"id": "p3", "platform_id": "p3", "difficulty": "Hard", "algorithm_tags": ["graphs", "bfs"], "quality_score": 8, "google_interview_relevance": 5, "sub_difficulty_level": 3},
            ],
        )

    resp = client.get("/skill-tree-v2/tags/overview", params={"top_problems_per_tag": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_problems"] == 3
    # At least arrays and graphs tags should be present
    tags = {t["tag"] for t in data["tags"]}
    assert "arrays" in tags and "graphs" in tags


def test_v2_search_problems_pagination(tmp_path):
    db_file = tmp_path / "v2_test_search.db"
    client, dbc = _init_app_and_db(str(db_file))

    with dbc.get_session() as s:
        _seed_problems(
            s,
            [
                {"id": f"arr_{i}", "platform_id": f"arr_{i}", "title": f"Array Problem {i}", "difficulty": "Easy", "algorithm_tags": ["arrays"], "quality_score": 5 + i, "google_interview_relevance": 5 + i, "sub_difficulty_level": 1}
                for i in range(15)
            ]
        )

    # Search "Array" with no skill_areas filter, expect SQL pagination
    resp = client.get(
        "/skill-tree-v2/search",
        params={"query": "Array", "page": 2, "page_size": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 2
    assert data["page_size"] == 5
    assert len(data["problems"]) == 5
