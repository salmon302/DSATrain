from fastapi.testclient import TestClient
import os

from src.api.main import app, _compute_source_url, _attach_metadata


def test_root_endpoint_payload():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data.get("message") == "DSA Training Platform API"
    assert data.get("version") == "4.0.0"
    assert data.get("status") == "active"
    assert "timestamp" in data


def test_cors_wildcard_no_credentials_header():
    # By default ALLOWED_ORIGINS is '*', and credentials are disabled
    client = TestClient(app)
    r = client.get("/", headers={"Origin": "http://example.com"})
    # With wildcard origins, starlette returns Access-Control-Allow-Origin: *
    assert r.headers.get("access-control-allow-origin") == "*"
    # Credentials header should be absent when allow_credentials is False
    assert "access-control-allow-credentials" not in {k.lower(): v for k, v in r.headers.items()}


def test_interactions_track_invalid_metadata_json():
    client = TestClient(app)
    resp = client.post(
        "/interactions/track",
        params={
            "user_id": "u1",
            "problem_id": "p1",
            "action": "viewed",
            "metadata": "not-json",
        },
    )
    assert resp.status_code == 400
    assert "Invalid metadata JSON" in resp.text


def test_interactions_track_unsupported_action():
    client = TestClient(app)
    resp = client.post(
        "/interactions/track",
        params={
            "user_id": "u2",
            "problem_id": "p2",
            "action": "foo",
        },
    )
    assert resp.status_code == 400
    assert "Unsupported action type" in resp.text


def test_compute_source_url_and_attach_metadata_unit():
    # Non-codeforces should return None
    assert _compute_source_url({"platform": "leetcode", "platform_id": "lc_123"}) is None

    # Codeforces invalid id format
    assert _compute_source_url({"platform": "codeforces", "platform_id": "cf_invalid"}) is None

    # Codeforces valid format
    p = {"platform": "codeforces", "platform_id": "cf_123_A"}
    url = _compute_source_url(p)
    assert url == "https://codeforces.com/contest/123/problem/A"

    # _attach_metadata should add metadata.source_url when missing
    enriched = _attach_metadata({
        "platform": "codeforces",
        "platform_id": "cf_999_B",
        "title": "Sample",
    })
    assert "metadata" in enriched
    assert enriched["metadata"].get("source_url") == "https://codeforces.com/contest/999/problem/B"
