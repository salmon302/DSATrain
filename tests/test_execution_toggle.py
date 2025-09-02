import os
from importlib import reload

import src.api.main as main


def test_execution_routes_toggle(monkeypatch):
    # By default should be enabled
    routes = [getattr(r, 'path', None) for r in main.app.routes]
    assert any(isinstance(p, str) and p.startswith('/execution') for p in routes)

    # Disable via env and reload module
    monkeypatch.setenv('DSATRAIN_DISABLE_CODE_EXECUTION', '1')
    reload(main)
    routes2 = [getattr(r, 'path', None) for r in main.app.routes]
    assert not any(isinstance(p, str) and p.startswith('/execution') for p in routes2)
