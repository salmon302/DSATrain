from fastapi.testclient import TestClient
import types
import asyncio

import src.api.main as main


def test_stats_endpoint_shape():
    client = TestClient(main.app)
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "database_stats" in data
    assert "quality_metrics" in data
    assert "last_updated" in data


class FakeResponse:
    def __init__(self, status_code: int, text: str = "", json_data=None, json_raises=False):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self._json_raises = json_raises

    def json(self):
        if self._json_raises:
            raise ValueError("invalid json")
        return self._json_data


class FakeAsyncClient:
    def __init__(self, response: FakeResponse, *args, **kwargs):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        return self._response


def test_skill_tree_proxy_upstream_error(monkeypatch):
    # Patch AsyncClient in main module to simulate upstream 500 error
    resp = FakeResponse(status_code=500, text="oops")
    monkeypatch.setattr(main, "httpx", types.SimpleNamespace(AsyncClient=lambda *a, **k: FakeAsyncClient(resp)))

    client = TestClient(main.app)
    r = client.get("/skill-tree-proxy/tags/overview", params={"top_problems_per_tag": 1})
    assert r.status_code == 500
    assert "Upstream error: oops" in r.text


def test_skill_tree_proxy_invalid_json(monkeypatch):
    # Patch AsyncClient in main module to simulate bad JSON body
    resp = FakeResponse(status_code=200, text="ok", json_data=None, json_raises=True)
    monkeypatch.setattr(main, "httpx", types.SimpleNamespace(AsyncClient=lambda *a, **k: FakeAsyncClient(resp)))

    client = TestClient(main.app)
    r = client.get("/skill-tree-proxy/tags/overview", params={"top_problems_per_tag": 1})
    assert r.status_code == 502
    assert "Invalid upstream response" in r.text
