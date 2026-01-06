import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL) if REDIS_URL else None

def cache_get(key: str):
    if not r:
        return None
    v = r.get(key)
    return json.loads(v) if v else None

def cache_set(key: str, value, ttl_seconds: int = 10):
    if not r:
        return
    r.setex(key, ttl_seconds, json.dumps(value))
