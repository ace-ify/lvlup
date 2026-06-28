from app.cache import ResponseCache
import time

def test_cache_fallback_operations():
    # Instantiate with use_redis=False to force in-memory local TTLCache fallback
    cache = ResponseCache(use_redis=False, ttl_seconds=2)
    
    # 1. Miss Lookup
    assert cache.get("What is RAG?") is None
    
    # 2. Set & Get
    cache.set("What is RAG?", "Retrieval-Augmented Generation")
    assert cache.get("What is RAG?") == "Retrieval-Augmented Generation"
    
    # 3. Cache Statistics
    stats = cache.stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["hit_rate"] == "50.0%"
    assert stats["backend"] == "in_memory"
    
    # 4. Invalidation (Delete)
    assert cache.delete("What is RAG?") is True
    assert cache.get("What is RAG?") is None
    
    # 5. Clear
    cache.set("Query A", "Answer A")
    cache.set("Query B", "Answer B")
    cache.clear()
    assert cache.get("Query A") is None
    assert cache.get("Query B") is None
    
    # 6. TTL Expiration
    cache.set("Expired Query", "Soon to disappear")
    time.sleep(2.5) # Wait for TTL of 2s to expire
    assert cache.get("Expired Query") is None
