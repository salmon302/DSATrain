"""
Advanced Caching Strategy for Skill Tree Performance
Multi-level caching for optimal performance with thousands of problems

Security note:
- By default, Redis values are serialized using Python pickle for broad compatibility.
- Pickle can execute arbitrary code when loading if the data store is compromised.
- To reduce risk in stricter environments, set DSATRAIN_CACHE_SERIALIZATION=json and
    only cache JSON-serializable objects. Non-serializable objects will not be stored in Redis.
"""

# Redis is optional. Import defensively so this module can load without it.
try:
    import redis as _redis
except Exception:  # pragma: no cover - optional dependency may be missing
    _redis = None
import json
import pickle
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass
import hashlib
import logging
import os

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuration for caching layers"""
    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 900  # 15 minutes
    long_term_ttl: int = 3600  # 1 hour
    enable_memory_cache: bool = True
    enable_redis_cache: bool = True
    max_memory_cache_size: int = 1000  # Max items in memory cache
    # Serialization mode for Redis values: 'pickle' (compatible, riskier) or 'json' (safer, limited types)
    serialization: str = "pickle"

class SkillTreeCacheManager:
    """
    Multi-level caching system:
    1. Memory cache (fastest, limited size)
    2. Redis cache (fast, persistent across requests)
    3. Database (slowest, always fresh)
    """
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        # Optional env override for serialization mode
        env_mode = os.getenv("DSATRAIN_CACHE_SERIALIZATION")
        if env_mode:
            self.config.serialization = env_mode.strip().lower()
        self.memory_cache = {}
        self.memory_cache_timestamps = {}
        self.redis_client = None
        
        # Initialize Redis if enabled
        if self.config.enable_redis_cache:
            try:
                if _redis is None:
                    raise RuntimeError("redis library not installed")
                self.redis_client = _redis.from_url(self.config.redis_url)
                self.redis_client.ping()  # Test connection
                logger.info("Redis cache initialized successfully")
                # Warn when running pickle + Redis (riskier) and inform current mode
                mode = (self.config.serialization or "pickle").lower()
                logger.info(f"Cache serialization mode: {mode}")
                if mode == "pickle":
                    logger.warning("Using pickle serialization with Redis enabled. This is flexible but riskier if Redis is compromised. Consider DSATRAIN_CACHE_SERIALIZATION=json in stricter environments.")
            except Exception as e:
                logger.warning(f"Redis cache unavailable: {str(e)}")
                self.config.enable_redis_cache = False

    # ----------------------- Serialization helpers -----------------------
    def _serialize_for_redis(self, data: Any) -> Optional[bytes]:
        mode = (self.config.serialization or "pickle").lower()
        if mode == "json":
            try:
                return json.dumps(data).encode("utf-8")
            except Exception as e:
                logger.warning(f"JSON serialization failed; not caching in Redis: {e}")
                return None
        # default: pickle
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.warning(f"Pickle serialization failed; not caching in Redis: {e}")
            return None

    def _deserialize_from_redis(self, raw: bytes) -> Optional[Any]:
        mode = (self.config.serialization or "pickle").lower()
        if mode == "json":
            try:
                return json.loads(raw.decode("utf-8"))
            except Exception as e:
                logger.warning(f"JSON deserialization failed for Redis data: {e}")
                return None
        # default: pickle
        try:
            return pickle.loads(raw)
        except Exception as e:
            logger.warning(f"Pickle deserialization failed for Redis data: {e}")
            return None
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate consistent cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"skill_tree:{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache (memory -> redis -> None)"""
        
        # 1. Check memory cache first
        if self.config.enable_memory_cache and self._is_memory_cache_valid(key):
            logger.debug(f"Cache HIT (memory): {key}")
            return self.memory_cache[key]
        
        # 2. Check Redis cache
        if self.config.enable_redis_cache and self.redis_client:
            try:
                redis_data = self.redis_client.get(key)
                if redis_data:
                    data = self._deserialize_from_redis(redis_data)
                    if data is None:
                        logger.debug(f"Cache REDIS DESERIALIZATION MISS: {key}")
                        return None
                    # Store in memory cache for faster future access
                    self._set_memory_cache(key, data)
                    logger.debug(f"Cache HIT (redis): {key}")
                    return data
            except Exception as e:
                logger.warning(f"Redis get error for {key}: {str(e)}")
        
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set data in cache (both memory and redis)"""
        ttl = ttl or self.config.default_ttl
        
        # 1. Set in memory cache
        if self.config.enable_memory_cache:
            self._set_memory_cache(key, data)
        
        # 2. Set in Redis cache
        if self.config.enable_redis_cache and self.redis_client:
            try:
                serialized_data = self._serialize_for_redis(data)
                if serialized_data is not None:
                    self.redis_client.setex(key, ttl, serialized_data)
                    logger.debug(f"Cache SET: {key} (TTL: {ttl}s, mode: {self.config.serialization})")
                else:
                    logger.debug(f"Cache SET SKIPPED (non-serializable under {self.config.serialization}): {key}")
            except Exception as e:
                logger.warning(f"Redis set error for {key}: {str(e)}")
    
    def delete(self, key: str) -> None:
        """Delete from all cache levels"""
        # Memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            del self.memory_cache_timestamps[key]
        
        # Redis cache
        if self.config.enable_redis_cache and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error for {key}: {str(e)}")
    
    def clear_pattern(self, pattern: str) -> None:
        """Clear all cache entries matching pattern"""
        # Memory cache
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            del self.memory_cache_timestamps[key]
        
        # Redis cache
        if self.config.enable_redis_cache and self.redis_client:
            try:
                keys = self.redis_client.keys(f"*{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis pattern delete error for {pattern}: {str(e)}")
    
    def _is_memory_cache_valid(self, key: str) -> bool:
        """Check if memory cache entry is still valid"""
        if key not in self.memory_cache:
            return False
        
        timestamp = self.memory_cache_timestamps.get(key)
        if not timestamp:
            return False
        
        return datetime.now() - timestamp < timedelta(seconds=self.config.default_ttl)
    
    def _set_memory_cache(self, key: str, data: Any) -> None:
        """Set data in memory cache with size limit"""
        # Clean up expired entries
        self._cleanup_memory_cache()
        
        # Enforce size limit (LRU eviction)
        if len(self.memory_cache) >= self.config.max_memory_cache_size:
            # Remove oldest entry
            oldest_key = min(self.memory_cache_timestamps.keys(), 
                           key=lambda k: self.memory_cache_timestamps[k])
            del self.memory_cache[oldest_key]
            del self.memory_cache_timestamps[oldest_key]
        
        self.memory_cache[key] = data
        self.memory_cache_timestamps[key] = datetime.now()
    
    def _cleanup_memory_cache(self) -> None:
        """Remove expired entries from memory cache"""
        now = datetime.now()
        expired_keys = [
            key for key, timestamp in self.memory_cache_timestamps.items()
            if now - timestamp > timedelta(seconds=self.config.default_ttl)
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
            del self.memory_cache_timestamps[key]


# Cache decorators for easy usage
def cached_skill_tree_method(cache_key_prefix: str, ttl: Optional[int] = None):
    """Decorator for caching skill tree methods"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache_manager._generate_cache_key(
                cache_key_prefix,
                args=args,
                kwargs=kwargs
            )
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(self, *args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = SkillTreeCacheManager()


class CachedSkillTreeAPI:
    """
    Skill Tree API with comprehensive caching
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    @cached_skill_tree_method("overview", ttl=900)  # 15 minutes
    def get_skill_tree_overview_cached(self, user_id: Optional[str] = None, top_problems: int = 5):
        """Cached skill tree overview"""
        from src.performance.skill_tree_optimizer import SkillTreePerformanceOptimizer
        
        optimizer = SkillTreePerformanceOptimizer(self.db)
        return optimizer.get_skill_area_summary_optimized()
    
    @cached_skill_tree_method("skill_area_problems", ttl=600)  # 10 minutes
    def get_skill_area_problems_cached(
        self, 
        skill_area: str, 
        page: int = 1, 
        page_size: int = 20,
        difficulty: Optional[str] = None,
        sort_by: str = "quality"
    ):
        """Cached skill area problems with pagination"""
        from src.performance.skill_tree_optimizer import SkillTreePerformanceOptimizer
        
        optimizer = SkillTreePerformanceOptimizer(self.db)
        return optimizer.get_paginated_problems_optimized(
            skill_area, page, page_size, difficulty, sort_by
        )
    
    @cached_skill_tree_method("search", ttl=300)  # 5 minutes
    def search_problems_cached(
        self,
        search_term: str,
        skill_areas: Optional[List[str]] = None,
        difficulties: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20
    ):
        """Cached problem search"""
        from src.performance.skill_tree_optimizer import SkillTreePerformanceOptimizer
        
        optimizer = SkillTreePerformanceOptimizer(self.db)
        return optimizer.search_problems_optimized(
            search_term, skill_areas, difficulties, None, page, page_size
        )
    
    @cached_skill_tree_method("statistics", ttl=1800)  # 30 minutes
    def get_statistics_cached(self):
        """Cached statistics"""
        from src.performance.skill_tree_optimizer import SkillTreePerformanceOptimizer
        
        optimizer = SkillTreePerformanceOptimizer(self.db)
        return optimizer.get_cached_statistics()
    
    def invalidate_caches(self, patterns: Optional[List[str]] = None):
        """Invalidate specific cache patterns or all skill tree caches"""
        if patterns:
            for pattern in patterns:
                cache_manager.clear_pattern(pattern)
        else:
            # Clear all skill tree caches
            cache_manager.clear_pattern("skill_tree:")


# Cache warming utilities
class CacheWarmer:
    """Pre-populate caches with frequently accessed data"""
    
    def __init__(self, cached_api: CachedSkillTreeAPI):
        self.api = cached_api
    
    def warm_skill_tree_caches(self):
        """Warm up all important caches"""
        logger.info("Starting cache warming process...")
        
        try:
            # 1. Warm overview cache
            self.api.get_skill_tree_overview_cached()
            
            # 2. Warm statistics cache
            self.api.get_statistics_cached()
            
            # 3. Warm first page of each skill area
            skill_areas = [
                "array_processing", "string_algorithms", "mathematical",
                "tree_algorithms", "graph_algorithms", "dynamic_programming",
                "sorting_searching", "advanced_structures"
            ]
            
            for skill_area in skill_areas:
                for difficulty in [None, "Easy", "Medium", "Hard"]:
                    self.api.get_skill_area_problems_cached(
                        skill_area=skill_area,
                        page=1,
                        difficulty=difficulty
                    )
            
            logger.info("Cache warming completed successfully")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {str(e)}")


# Cache monitoring utilities
class CacheMonitor:
    """Monitor cache performance and statistics"""
    
    def __init__(self, cache_manager: SkillTreeCacheManager):
        self.cache_manager = cache_manager
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        stats = {
            "memory_cache": {
                "size": len(self.cache_manager.memory_cache),
                "max_size": self.cache_manager.config.max_memory_cache_size,
                "hit_rate": "N/A"  # Would need hit/miss counters
            },
            "redis_cache": {
                "available": self.cache_manager.config.enable_redis_cache,
                "connected": bool(self.cache_manager.redis_client)
            },
            "config": {
                "default_ttl": self.cache_manager.config.default_ttl,
                "enable_memory_cache": self.cache_manager.config.enable_memory_cache,
                "enable_redis_cache": self.cache_manager.config.enable_redis_cache
            }
        }
        
        # Get Redis info if available
        if self.cache_manager.redis_client:
            try:
                redis_info = self.cache_manager.redis_client.info()
                stats["redis_cache"]["memory_usage"] = redis_info.get("used_memory_human", "N/A")
                stats["redis_cache"]["connected_clients"] = redis_info.get("connected_clients", 0)
            except Exception as e:
                logger.warning(f"Could not get Redis stats: {str(e)}")
        
        return stats


# Usage example:
"""
# Initialize caching system
from src.models.database import DatabaseConfig

db_config = DatabaseConfig("sqlite:///dsatrain_phase4.db")
db = db_config.get_session()

# Create cached API
cached_api = CachedSkillTreeAPI(db)

# Warm caches (run on server startup)
warmer = CacheWarmer(cached_api)
warmer.warm_skill_tree_caches()

# Use cached methods
overview = cached_api.get_skill_tree_overview_cached()
problems, total, has_next = cached_api.get_skill_area_problems_cached("array_processing")

# Monitor cache performance
monitor = CacheMonitor(cache_manager)
stats = monitor.get_cache_stats()
print(json.dumps(stats, indent=2))
"""
