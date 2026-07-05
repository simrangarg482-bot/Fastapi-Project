import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)


def get_cached_prediction(key: str):
    value = redis_client.get(key)
    return json.loads(value) if value else None


def set_cached_prediction(key: str, value):
    redis_client.set(key, json.dumps(value)) 