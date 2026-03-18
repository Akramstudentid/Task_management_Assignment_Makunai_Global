import json
import redis

REDIS_AVAILABLE = False
r = None

try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()  # Test connection
    REDIS_AVAILABLE = True
except redis.ConnectionError:
    REDIS_AVAILABLE = False


def get_cache(key: str):
    if not REDIS_AVAILABLE:
        return None
    try:
        data = r.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


def set_cache(key: str, value):
    if not REDIS_AVAILABLE:
        return
    try:
        r.setex(key, 60, json.dumps(value))  # cache for 60 seconds
    except Exception:
        pass