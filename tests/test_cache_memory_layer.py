import time
from src.performance.caching_strategy import SkillTreeCacheManager, CacheConfig


def test_memory_cache_set_get_and_ttl():
    cfg = CacheConfig(enable_redis_cache=False, default_ttl=1, max_memory_cache_size=10)
    cm = SkillTreeCacheManager(cfg)

    key = 'skill_tree:test:abc'
    cm.set(key, {'v': 1})
    assert cm.get(key) == {'v': 1}

    # Wait for TTL expiry and cleanup
    time.sleep(1.2)
    # Access should trigger MISS after TTL
    assert cm.get(key) is None


def test_memory_cache_lru_eviction():
    cfg = CacheConfig(enable_redis_cache=False, default_ttl=30, max_memory_cache_size=3)
    cm = SkillTreeCacheManager(cfg)

    # Fill cache over capacity
    for i in range(5):
        cm.set(f'k{i}', i)
    # Size is capped at 3; oldest keys should have been removed
    present = [k for k in ['k0','k1','k2','k3','k4'] if cm.get(k) is not None]
    assert len(present) <= 3
