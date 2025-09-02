from fastapi.testclient import TestClient
import types
import urllib.parse

import src.api.main as main


class CaptureClient:
    def __init__(self):
        self.captured = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        self.captured = (url, params)
        class R:
            status_code = 200
            def json(self):
                return {"problems": [], "count": 0}
        return R()


def test_proxy_param_passthrough(monkeypatch):
    cap = CaptureClient()
    monkeypatch.setattr(main, "httpx", types.SimpleNamespace(AsyncClient=lambda *a, **k: cap))

    client = TestClient(main.app)
    params = {
        "page": 2,
        "page_size": 25,
        "sort_by": "quality",
        "sort_order": "asc",
        "difficulty": "Hard",
        "query": "two sum",
        "platform": "leetcode",
        "title_match": "prefix",
    }
    r = client.get("/skill-tree-proxy/skill-area/arrays/problems", params=params)
    assert r.status_code == 200

    url, sent = cap.captured
    # Ensure correct path encoding & param propagation
    assert url.endswith("skill-area/arrays/problems")
    for k, v in {k: params[k] for k in ["page","page_size","sort_by","sort_order","difficulty","query","platform","title_match"]}.items():
        assert sent.get(k) == v
