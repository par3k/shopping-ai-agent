from functools import lru_cache

import redis

from app.config import load_settings


@lru_cache
def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(load_settings().redis_url, decode_responses=True)
