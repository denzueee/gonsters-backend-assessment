import json
import logging
from functools import wraps

from flask import Response, jsonify, request

from app.database import get_redis_client

logger = logging.getLogger(__name__)


def cache_response(timeout=300, key_prefix="view"):  # noqa: C901
    """
    Decorator to cache Flask response in Redis.
    Only caches 200 OK responses.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            redis_client = get_redis_client()
            if not redis_client:
                return f(*args, **kwargs)

            # Create cache key
            # Uses path and query string to differentiate requests
            query = request.query_string.decode("utf-8")
            key = f"cache:{key_prefix}:{request.path}"
            if query:
                key += f":{query}"

            try:
                # Check cache
                cached_val = redis_client.get(key)
                if cached_val:
                    logger.debug(f"Cache HIT for {key}")
                    # Return cached JSON
                    return jsonify(json.loads(cached_val)), 200

                # Execute view function
                response = f(*args, **kwargs)

                # Check if response is cacheable
                # Typically Flask returns: (Response/dict, status_code)
                # Or just Response object

                resp_obj = None
                status = 200

                if isinstance(response, tuple):
                    resp_obj = response[0]
                    if len(response) > 1:
                        status = response[1]
                else:
                    resp_obj = response

                # Only cache 200 OK
                if status == 200:
                    data = None
                    if isinstance(resp_obj, Response):
                        data = resp_obj.get_json()

                    if data:
                        redis_client.setex(key, timeout, json.dumps(data))
                        logger.debug(f"Cached response for {key}")

                return response

            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
                # Fail gracefully, behave as if no cache
                return f(*args, **kwargs)

        return decorated_function

    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache keys matching a pattern.
    Pattern example: 'cache:config:*'
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            return

        keys = redis_client.keys(key_pattern)
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys for pattern {key_pattern}")

    except Exception as e:
        logger.error(f"Cache invalidation error: {str(e)}")
