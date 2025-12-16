"""
Modul Koneksi Redis
Menangani koneksi dan operasi dasar caching dengan Redis
"""

import logging

import redis

from app.config import get_config

logger = logging.getLogger(__name__)

redis_client = None


def init_redis():
    """
    Inisialisasi koneksi Redis dengan retry logic

    Returns:
        Redis: Client Redis atau None jika gagal
    """
    global redis_client
    config = get_config()

    # Retry dengan exponential backoff
    max_retries = 2
    base_timeout = 2

    for attempt in range(max_retries):
        try:
            timeout = base_timeout * (attempt + 1)  # 2s, 4s
            client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=timeout,
                socket_timeout=timeout,
            )
            client.ping()
            logger.info("Connected to Redis successfully")
            redis_client = client
            return redis_client
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                logger.debug(f"Redis connection attempt {attempt + 1} failed, retrying...")
            else:
                logger.warning(f"Redis connection failed after {max_retries} attempts: {e}. Caching will be disabled.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            return None

    return None


def get_redis_client():
    """
    Mengambil client Redis. Mencoba reconnect jika belum terhubung.

    Returns:
        Redis: Client Redis atau None
    """

    if redis_client is None:
        return init_redis()

    try:
        redis_client.ping()
        return redis_client
    except redis.ConnectionError:
        logger.warning("Temporary Redis connection loss, self-healing retry is initiated")
        return init_redis()


def blacklist_token(token, ttl=3600):
    """
    Menambahkan token ke blacklist

    Args:
        token (str): JWT token string
        ttl (int): Time to live dalam detik (default: 1 jam)
    """
    client = get_redis_client()
    if client:
        try:
            # Gunakan prefix 'bl_' untuk blacklist
            key = f"bl_{token}"
            client.setex(key, ttl, "revoked")
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    return False


def is_token_blacklisted(token):
    """
    Memeriksa apakah token ada di blacklist

    Args:
        token (str): JWT token string

    Returns:
        bool: True jika token di-blacklist, False jika tidak
    """
    client = get_redis_client()
    if client:
        try:
            key = f"bl_{token}"
            return client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
    return False
