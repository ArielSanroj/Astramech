#!/usr/bin/env python3
"""
Cache management system for xcontentbot.
Provides LRU cache for post data and other frequently accessed information.
"""

import time
import logging
from typing import Dict, Any, Optional
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU cache for post data with TTL support."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to store
            ttl: Time to live in seconds
        """
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self.cache:
                return None
            
            # Check TTL
            if time.time() - self.timestamps[key] > self.ttl:
                self.delete(key)
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def set(self, key: str, value: Any):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                self.cache[key] = value
                self.timestamps[key] = time.time()
                
                # Evict oldest if over max_size
                if len(self.cache) > self.max_size:
                    oldest = next(iter(self.cache))
                    self.delete(oldest)
    
    def delete(self, key: str):
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
    
    def clear(self):
        """Clear all cached data."""
        with self._lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for timestamp in self.timestamps.values()
                if current_time - timestamp > self.ttl
            )
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
                "expired_items": expired_count,
                "hit_ratio": getattr(self, '_hits', 0) / max(getattr(self, '_accesses', 1), 1)
            }


class PostCache:
    """Specialized cache for post data."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize post cache.
        
        Args:
            max_size: Maximum number of posts to cache
            ttl: Time to live in seconds
        """
        self.cache = LRUCache(max_size, ttl)
        self._hits = 0
        self._misses = 0
        self._accesses = 0
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get post data from cache.
        
        Args:
            post_id: Post ID
            
        Returns:
            Post data or None if not cached
        """
        self._accesses += 1
        result = self.cache.get(post_id)
        
        if result is not None:
            self._hits += 1
            logger.debug(f"Cache hit for post {post_id}")
        else:
            self._misses += 1
            logger.debug(f"Cache miss for post {post_id}")
        
        return result
    
    def set_post(self, post_id: str, post_data: Dict[str, Any]):
        """
        Cache post data.
        
        Args:
            post_id: Post ID
            post_data: Post data to cache
        """
        self.cache.set(post_id, post_data)
        logger.debug(f"Cached post {post_id}")
    
    def mark_processed(self, post_id: str):
        """
        Mark post as processed in cache.
        
        Args:
            post_id: Post ID
        """
        post_data = self.get_post(post_id)
        if post_data:
            post_data['processed'] = True
            post_data['processed_at'] = time.time()
            self.set_post(post_id, post_data)
    
    def is_processed(self, post_id: str) -> bool:
        """
        Check if post has been processed.
        
        Args:
            post_id: Post ID
            
        Returns:
            True if post has been processed
        """
        post_data = self.get_post(post_id)
        return post_data is not None and post_data.get('processed', False)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.cache.get_stats()
        stats.update({
            "hits": self._hits,
            "misses": self._misses,
            "accesses": self._accesses,
            "hit_ratio": self._hits / max(self._accesses, 1)
        })
        return stats


# Global cache instances
post_cache = PostCache(max_size=1000, ttl=3600)
comment_cache = LRUCache(max_size=500, ttl=1800)  # 30 minutes for comments


def get_cached_post(post_id: str) -> Optional[Dict[str, Any]]:
    """Get post from cache."""
    return post_cache.get_post(post_id)


def cache_post(post_id: str, post_data: Dict[str, Any]):
    """Cache post data."""
    post_cache.set_post(post_id, post_data)


def mark_post_processed(post_id: str):
    """Mark post as processed."""
    post_cache.mark_processed(post_id)


def is_post_processed(post_id: str) -> bool:
    """Check if post has been processed."""
    return post_cache.is_processed(post_id)


def get_cache_stats() -> Dict[str, Any]:
    """Get all cache statistics."""
    return {
        "post_cache": post_cache.get_stats(),
        "comment_cache": comment_cache.get_stats()
    }


def clear_all_caches():
    """Clear all caches."""
    post_cache.cache.clear()
    comment_cache.clear()
    logger.info("All caches cleared")
