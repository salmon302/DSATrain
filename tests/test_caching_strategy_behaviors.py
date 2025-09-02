import importlib
import time

import pytest


def fresh_module(monkeypatch, **env):
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    mod = importlib.import_module("src.performance.caching_strategy")
    importlib.reload(mod)
    return mod


def test_clear_pattern_and_delete_memory_only(monkeypatch):
    mod = fresh_module(monkeypatch, DSATRAIN_CACHE_SERIALIZATION="pickle")
    cache = mod.SkillTreeCacheManager(mod.CacheConfig(enable_redis_cache=False))

    cache.set("skill_tree:a:1", 1)
    cache.set("skill_tree:a:2", 2)
    cache.set("skill_tree:b:1", 3)

    assert cache.get("skill_tree:a:1") == 1
    cache.clear_pattern("skill_tree:a:")
    assert cache.get("skill_tree:a:1") is None
    assert cache.get("skill_tree:a:2") is None
    assert cache.get("skill_tree:b:1") == 3

    cache.delete("skill_tree:b:1")
    assert cache.get("skill_tree:b:1") is None


def test_cache_decorator_ttl_and_memoization(monkeypatch):
    mod = fresh_module(monkeypatch, DSATRAIN_CACHE_SERIALIZATION="pickle")
    # Create a local cache manager to avoid interference with global
    cm = mod.SkillTreeCacheManager(mod.CacheConfig(enable_redis_cache=False, default_ttl=1))

    calls = {"count": 0}

    class Dummy:
        def __init__(self):
            self.db = None

        def compute(self, x):
            calls["count"] += 1
            return x * 2

    # Manually construct a decorator instance wired to the global cache_manager in module
    # To control it, monkeypatch the module-level cache_manager to our local cm
    monkeypatch.setattr(mod, "cache_manager", cm, raising=True)

    Dummy.cached = mod.cached_skill_tree_method("dummy", ttl=1)(Dummy.compute)

    d = Dummy()
    # First call populates cache
    assert d.cached(3) == 6
    assert calls["count"] == 1
    # Second call hits cache
    assert d.cached(3) == 6
    assert calls["count"] == 1
    # After TTL expires, function called again
    time.sleep(1.2)
    assert d.cached(3) == 6
    assert calls["count"] == 2


def test_cache_monitor_stats(monkeypatch):
    mod = fresh_module(monkeypatch)
    cm = mod.SkillTreeCacheManager(mod.CacheConfig(enable_redis_cache=False))
    mon = mod.CacheMonitor(cm)
    # Prime with one entry
    cm.set("k", {"v": 1})
    stats = mon.get_cache_stats()
    assert "memory_cache" in stats and "redis_cache" in stats and "config" in stats
    assert stats["memory_cache"]["size"] >= 1
