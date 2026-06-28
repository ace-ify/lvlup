import redis
import json
import hashlib
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, db=0, protocol=2)


class PostRequest(BaseModel):
    post_id: int


def make_cache_key(post_id: int):
    raw = f"external_api:post_{post_id}"
    return hashlib.sha256(raw.encode()).hexdigest()


@app.post('/get-post')
async def get_post(data: PostRequest):
    cache_key = make_cache_key(data.post_id)

    cached_data = redis_client.get(cache_key)
    if cached_data:
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        print(f"[{now}] Served from Redis cache!")
        post_data = json.loads(cached_data)
        post_data['served_at'] = now
        post_data['source'] = 'Redis Cache'
        return post_data
    
    print('Calling external API...')
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://jsonplaceholder.typicode.com/posts/{data.post_id}")
        if response.status_code != 200:
            return {'error': 'Post not found!'}
        
    post_data = response.json()
    
    from datetime import datetime
    fetched_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    post_data['fetched_at'] = fetched_time
    post_data['source'] = 'External API'
    
    redis_client.setex(cache_key, 600, json.dumps(post_data))
    print(f"[{fetched_time}] Fetched from External API and stored in Cache!")
    return post_data