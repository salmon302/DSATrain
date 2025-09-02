import importlib


def test_cache_serialization_env_override_json(monkeypatch):
    # Force JSON mode via env
    monkeypatch.setenv("DSATRAIN_CACHE_SERIALIZATION", "json")
    # Reload module to apply env at import/instantiation time
    mod = importlib.import_module("src.performance.caching_strategy")
    importlib.reload(mod)

    cache = mod.SkillTreeCacheManager(mod.CacheConfig(enable_redis_cache=False))
    # Set/get through memory cache only, but verify config picks up json
    key = "skill_tree:test:env_json"
    data = {"a": 1, "b": [1, 2, 3]}
    cache.set(key, data, ttl=5)
    assert cache.get(key) == data
    assert cache.config.serialization == "json"


def test_serialize_non_json_skips_redis(monkeypatch):
    # Ensure we use JSON serialization and simulate having a redis client object that won't be used
    monkeypatch.setenv("DSATRAIN_CACHE_SERIALIZATION", "json")
    mod = importlib.import_module("src.performance.caching_strategy")
    importlib.reload(mod)

    # Build manager with a fake redis client to capture setex calls
    cfg = mod.CacheConfig(enable_redis_cache=True)
    cache = mod.SkillTreeCacheManager(cfg)

    class FakeRedis:
        def __init__(self):
            self.setex_called = False
        def ping(self):
            pass
        def get(self, key):
            return None
        def setex(self, key, ttl, value):
            self.setex_called = True
        def delete(self, *args, **kwargs):
            pass
        def keys(self, *args, **kwargs):
            return []

    cache.redis_client = FakeRedis()
    # Force-enable redis cache to exercise the set path with our fake client
    cache.config.enable_redis_cache = True

    # A non-JSON-serializable object (e.g., set)
    key = "skill_tree:test:non_json"
    data = {"x", "y"}
    cache.set(key, data, ttl=5)

    # In JSON mode, Redis set should be skipped
    assert cache.redis_client.setex_called is False
    # Memory cache still holds the object
    assert cache.get(key) == data
