import redis
from app.core.config import settings

def get_redis_client():
    try:
        client = redis.Redis(
            host=settings.redis_host, 
            port=settings.redis_port, 
            decode_responses=True,
            protocol=2
        )
        client.ping() # Connection test
        return client
    except redis.ConnectionError:
        print("Warning: Redis is not running. Caching is disabled.")
        return None

redis_client = get_redis_client()
