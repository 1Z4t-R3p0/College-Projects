from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import os
import time

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)

# 15 minutes auto-unblock
BLOCK_TIME = 900
FAILED_ATTEMPTS_LIMIT = 50

def setup_limiter(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=redis_url,
        strategy="fixed-window",
    )
    return limiter

def is_ip_blocked(ip):
    # Check if the IP exists in the 'blocked_ips' Redis set
    return redis_client.exists(f"blocked:{ip}")

def block_ip(ip):
    # Set with an expiration of BLOCK_TIME (10 mins)
    redis_client.setex(f"blocked:{ip}", BLOCK_TIME, "1")

def record_failed_attempt(ip):
    # Increment failed attempts for IP within a moving window
    key = f"failed:{ip}"
    attempts = redis_client.incr(key)
    if attempts == 1:
        # Expire tracking after 10 minutes to match block logic
        redis_client.expire(key, BLOCK_TIME)
        
    if attempts >= FAILED_ATTEMPTS_LIMIT:
        block_ip(ip)
        
    return attempts
