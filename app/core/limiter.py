from slowapi import Limiter
from slowapi.util import get_remote_address

# Default limiter — keys by client IP address
# Uses Redis so limits survive restarts and work across multiple workers
limiter = Limiter(
    key_func=get_remote_address,
    # storage_uri is picked up from REDIS_URL via config in main.py
)
