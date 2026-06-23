#!/usr/bin/env python3
"""
Tests for cache management system.
"""

import pytest
import time
from cache_manager import LRUCache, PostCache, get_cached_post, cache_post, mark_post_processed, is_post_processed


class TestLRUCache:
    """Test LRU cache functionality."""
    
    def test_basic_operations(self):
        """Test basic cache operations."""
        cache = LRUCache(max_size=3, ttl=60)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test non-existent key
        assert cache.get("key2") is None
    
    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = LRUCache(max_size=3, ttl=0.1)  # 100ms TTL
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(0.2)
        assert cache.get("key1") is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when max size exceeded."""
        cache = LRUCache(max_size=2, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_lru_access_order(self):
        """Test that accessing a key moves it to end."""
        cache = LRUCache(max_size=2, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Access key1 to move it to end
        cache.get("key1")
        
        # Add new key, should evict key2
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_delete(self):
        """Test key deletion."""
        cache = LRUCache(max_size=3, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.delete("key1")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_clear(self):
        """Test cache clearing."""
        cache = LRUCache(max_size=3, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0
    
    def test_stats(self):
        """Test cache statistics."""
        cache = LRUCache(max_size=3, ttl=60)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 3
        assert stats["ttl"] == 60


class TestPostCache:
    """Test post cache functionality."""
    
    def test_post_operations(self):
        """Test post cache operations."""
        cache = PostCache(max_size=3, ttl=60)
        
        post_data = {
            "id": "123",
            "url": "https://x.com/user/status/123",
            "text": "Test post",
            "author": "testuser"
        }
        
        # Test caching post
        cache.set_post("123", post_data)
        cached_post = cache.get_post("123")
        assert cached_post == post_data
        
        # Test marking as processed
        cache.mark_processed("123")
        processed_post = cache.get_post("123")
        assert processed_post["processed"] is True
        assert "processed_at" in processed_post
        
        # Test checking if processed
        assert cache.is_processed("123") is True
        assert cache.is_processed("456") is False
    
    def test_post_cache_stats(self):
        """Test post cache statistics."""
        cache = PostCache(max_size=3, ttl=60)
        
        # Add some posts
        cache.set_post("123", {"id": "123"})
        cache.set_post("456", {"id": "456"})
        
        # Access posts
        cache.get_post("123")
        cache.get_post("456")
        cache.get_post("789")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["accesses"] == 3
        assert stats["hit_ratio"] == 2/3


class TestGlobalCacheFunctions:
    """Test global cache functions."""
    
    def test_global_functions(self):
        """Test global cache functions."""
        from cache_manager import post_cache
        
        # Clear cache first
        post_cache.cache.clear()
        
        post_data = {
            "id": "123",
            "url": "https://x.com/user/status/123",
            "text": "Test post"
        }
        
        # Test caching
        cache_post("123", post_data)
        cached = get_cached_post("123")
        assert cached == post_data
        
        # Test marking as processed
        mark_post_processed("123")
        assert is_post_processed("123") is True
        assert is_post_processed("456") is False
    
    def test_cache_stats(self):
        """Test cache statistics."""
        from cache_manager import get_cache_stats
        
        stats = get_cache_stats()
        assert "post_cache" in stats
        assert "comment_cache" in stats
        
        post_stats = stats["post_cache"]
        assert "size" in post_stats
        assert "hits" in post_stats
        assert "misses" in post_stats
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        from cache_manager import clear_all_caches
        
        # Add some data
        cache_post("123", {"id": "123"})
        
        # Clear all caches
        clear_all_caches()
        
        # Should be empty
        assert get_cached_post("123") is None


class TestCacheConcurrency:
    """Test cache concurrency."""
    
    def test_thread_safety(self):
        """Test that cache is thread-safe."""
        import threading
        
        cache = LRUCache(max_size=100, ttl=60)
        results = []
        
        def worker(thread_id):
            for i in range(10):
                key = f"key_{thread_id}_{i}"
                value = f"value_{thread_id}_{i}"
                cache.set(key, value)
                result = cache.get(key)
                results.append((thread_id, i, result == value))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check that all operations succeeded
        assert all(success for _, _, success in results)
        assert len(results) == 50  # 5 threads * 10 operations each
