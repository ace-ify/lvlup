import hashlib
import json
import zlib
import logging
import time
from typing import Optional, Any
import redis
from cachetools import TTLCache
import threading
from datetime import datetime, date
from decimal import Decimal
import uuid
from app.config import get_settings

logger = logging.getLogger(__name__)

class CacheJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle complex types commonly found in RAG payloads."""
    def default(self, obj: Any) -> Any:
        # Support Pydantic models (v1 and v2)
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="ignore")
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)

class ResponseCache:
    """
    Production-hardened Caching Layer.
    Uses Redis for shared, persistent caching with TTL management.
    Falls back gracefully to a thread-safe, size-bounded in-memory TTLCache if Redis is unavailable.
    Supports namespaces, compression, serialization, reconnection, and batched invalidation.
    """

    def __init__(
        self, 
        redis_url: Optional[str] = None, 
        use_redis: Optional[bool] = None, 
        ttl_seconds: int = 300,
        namespace: str = "chat",
        max_local_entries: int = 10000,
        compression_threshold_bytes: int = 4096  # Compress entries > 4KB for LLM workloads
    ):
        settings = get_settings()
        self.ttl = ttl_seconds
        self.use_redis = use_redis if use_redis is not None else settings.use_redis
        self.redis_url = redis_url if redis_url is not None else settings.redis_url
        self._allow_redis = self.use_redis and bool(self.redis_url)
        self.namespace = namespace.strip(":")
        self.compression_threshold = compression_threshold_bytes
        
        self.redis_client: Optional[redis.Redis] = None
        self._last_reconnect_attempt = 0.0
        
        # Thread-safe, bounded-size local cache fallback using RLock to prevent re-entrant deadlocks
        self._local_cache = TTLCache(maxsize=max_local_entries, ttl=self.ttl)
        self._local_lock = threading.RLock()
        
        # Local stats fallback (Redis stats are stored on Redis directly)
        self._local_hits = 0
        self._local_misses = 0
        
        if self.use_redis and self.redis_url:
            self._establish_connection()

    def _establish_connection(self) -> None:
        """Helper to initialize the Redis connection client."""
        try:
            # Initialize Redis connection with RESP2 protocol compatibility
            # decode_responses is False because we are storing binary/compressed data
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=False,
                socket_connect_timeout=2.0,
                protocol=2
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"Successfully connected to Redis cache backend. Namespace: {self.namespace}")
        except redis.RedisError as e:
            logger.exception(f"Failed to connect to Redis at {self.redis_url}: {e}. Falling back to in-memory TTLCache.")
            self.redis_client = None
            self.use_redis = False

    def _check_reconnect(self) -> None:
        """Attempt to reconnect to Redis if the connection was previously lost, throttled to once per 60 seconds."""
        if self._allow_redis and not self.use_redis and self.redis_url:
            now = time.time()
            if now - self._last_reconnect_attempt > 60.0:
                self._last_reconnect_attempt = now
                logger.info("Attempting to reconnect to Redis cache backend...")
                self._establish_connection()

    def _make_key(self, query: str) -> str:
        """Create a normalized, whitespace-collapsed cache key."""
        # Collapse multiple spaces inside the string and strip external spaces
        normalized = " ".join(query.lower().split())
        hash_val = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        # Namespaced isolation
        return f"{self.namespace}:entry:{hash_val}"

    def _serialize_and_compress(self, data: Any) -> bytes:
        """Serialize data to JSON and compress using zlib if it exceeds the threshold."""
        serialized = json.dumps(data, cls=CacheJSONEncoder).encode("utf-8")
        if len(serialized) > self.compression_threshold:
            # Prepend a byte flag \x01 to indicate compressed content
            return b"\x01" + zlib.compress(serialized)
        # Prepend \x00 to indicate uncompressed content
        return b"\x00" + serialized

    def _decompress_and_deserialize(self, payload: bytes) -> Any:
        """Decompress zlib payload and deserialize from JSON safely, failing open on corruption."""
        if not payload:
            return None
        try:
            compression_flag = payload[0:1]
            raw_data = payload[1:]
            
            if compression_flag == b"\x01":
                decompressed = zlib.decompress(raw_data)
                return json.loads(decompressed.decode("utf-8"))
            elif compression_flag == b"\x00":
                return json.loads(raw_data.decode("utf-8"))
            else:
                # Fallback for old unflagged plain string cache entries
                return json.loads(payload.decode("utf-8"))
        except (zlib.error, json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.exception(f"Cache payload corruption detected: {e}. Treating as cache miss to fail open.")
            return None

    def get(self, query: str) -> Optional[Any]:
        """
        Get cached response if it exists and hasn't expired.
        Returns None on cache miss.
        """
        self._check_reconnect()
        key = self._make_key(query)

        # 1. Redis Caching Flow
        if self.redis_client:
            try:
                payload = self.redis_client.get(key)
                if payload is not None:
                    # Increment hits in Redis to keep stats persistent across instances
                    self.redis_client.incr(f"{self.namespace}:metrics:hits")
                    decoded = self._decompress_and_deserialize(payload)
                    if decoded is not None:
                        return decoded
                else:
                    self.redis_client.incr(f"{self.namespace}:metrics:misses")
                    return None
            except redis.RedisError:
                # Disable Redis dynamically to avoid log spamming on consecutive connection errors
                logger.exception("Redis connection lost during get(). Disabling Redis backend for this runtime session.")
                self.redis_client = None
                self.use_redis = False

        # 2. Local In-Memory Fallback Flow
        with self._local_lock:
            # TTLCache automatically handles expiration and removal internally
            if key in self._local_cache:
                self._local_hits += 1
                return self._local_cache[key]
            else:
                self._local_misses += 1
                return None

    def set(self, query: str, response: Any) -> None:
        """Cache a response."""
        self._check_reconnect()
        key = self._make_key(query)

        # 1. Redis Caching Flow
        if self.redis_client:
            try:
                payload = self._serialize_and_compress(response)
                self.redis_client.setex(key, self.ttl, payload)
                return
            except redis.RedisError:
                logger.exception("Redis connection lost during set(). Disabling Redis backend for this runtime session.")
                self.redis_client = None
                self.use_redis = False

        # 2. Local In-Memory Fallback Flow
        with self._local_lock:
            # Save the value directly in the TTLCache (expiration is handled natively)
            self._local_cache[key] = response

    def delete(self, query: str) -> bool:
        """Invalidate a specific cache key."""
        key = self._make_key(query)
        deleted = False

        if self.redis_client:
            try:
                deleted = bool(self.redis_client.delete(key))
            except redis.RedisError:
                logger.exception("Redis connection lost during delete(). Disabling Redis backend.")
                self.redis_client = None
                self.use_redis = False

        with self._local_lock:
            if key in self._local_cache:
                del self._local_cache[key]
                deleted = True

        return deleted

    def clear(self) -> None:
        """Clear the entire cache database for this namespace using batch pipelines."""
        if self.redis_client:
            try:
                # Batch delete keys to prevent freezing Redis
                pipeline = self.redis_client.pipeline()
                batch_size = 500
                count = 0
                
                for key in self.redis_client.scan_iter(match=f"{self.namespace}:entry:*"):
                    pipeline.delete(key)
                    count += 1
                    if count % batch_size == 0:
                        pipeline.execute()
                
                if count % batch_size != 0:
                    pipeline.execute()
                
                # Reset metrics
                self.redis_client.delete(f"{self.namespace}:metrics:hits", f"{self.namespace}:metrics:misses")
                logger.info(f"Redis cache cleared for namespace: {self.namespace} (Deleted {count} keys)")
            except redis.RedisError:
                logger.exception("Redis connection lost during clear(). Disabling Redis backend.")
                self.redis_client = None
                self.use_redis = False

        with self._local_lock:
            self._local_cache.clear()
            logger.info("Local in-memory TTLCache cleared.")

    @property
    def stats(self) -> dict:
        """Cache performance statistics."""
        if self.redis_client:
            try:
                hits = int(self.redis_client.get(f"{self.namespace}:metrics:hits") or 0)
                misses = int(self.redis_client.get(f"{self.namespace}:metrics:misses") or 0)
                
                total = hits + misses
                hit_rate = hits / total if total > 0 else 0.0
                
                return {
                    "hits": hits,
                    "misses": misses,
                    "hit_rate": f"{hit_rate:.1%}",
                    "cached_entries": "N/A (O(N) Redis scan disabled for performance)",
                    "backend": "redis",
                    "namespace": self.namespace
                }
            except redis.RedisError:
                logger.exception("Redis connection lost during stats(). Disabling Redis backend.")
                self.redis_client = None
                self.use_redis = False


        # Local stats fallback
        total = self._local_hits + self._local_misses
        hit_rate = self._local_hits / total if total > 0 else 0.0
        return {
            "hits": self._local_hits,
            "misses": self._local_misses,
            "hit_rate": f"{hit_rate:.1%}",
            "cached_entries": len(self._local_cache),
            "backend": "in_memory",
            "namespace": self.namespace
        }
