import os
from dotenv import load_dotenv
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

async def init_redis(app):
    try:
        redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        await redis.ping()  # Test the connection
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        print("Redis connection successful")
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        print("Caching will be disabled")