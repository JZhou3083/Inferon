import redis 
import json 
import hashlib
# 注意这里的 host 应该是 docker-compose 中定义的服务名 "redis"，
# 而不是 "localhost",因为应用容器和 Redis 容器是通过 Docker 网络连接的。
redis_client = redis.Redis(host="redis", port=6379, db=0) 

def get_cache(key:str):
    data = redis_client.get(key)
    if isinstance(data, bytes):
        return json.loads(data.decode('utf-8'))
    return None

def set_cache(key:str, value,ttl:int =300):
    redis_client.setex(key,ttl,json.dumps(value))

# =========================================================
# CACHE KEY
# =========================================================

def build_cache_key(prompt: str) -> str:
    """
    Creates a stable hash-based cache key for a prompt.

    We hash instead of storing raw prompts to:
    - avoid huge Redis keys
    - normalize long prompts safely
    """
    hashed = hashlib.sha256(prompt.encode()).hexdigest()
    return f"llm:{hashed}"
