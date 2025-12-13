"""
Modul Koneksi Redis
Menangani koneksi dan operasi dasar caching dengan Redis
"""

import redis
import logging
from app.config import get_config

logger = logging.getLogger(__name__)

redis_client = None


def init_redis():
    """
    Inisialisasi koneksi Redis
    
    Returns:
        Redis: Client Redis atau None jika gagal
    """
    global redis_client
    config = get_config()
    
    try:
        client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            password=config.REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=1
        )
        client.ping()
        logger.info("Connected to Redis successfully")
        redis_client = client
        return redis_client
    except redis.ConnectionError as e:
        logger.warning(f"Redis connection failed: {e}. Caching will be disabled.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis: {e}")
        return None


def get_redis_client():
    """
    Mengambil client Redis. Mencoba reconnect jika belum terhubung.
    
    Returns:
        Redis: Client Redis atau None
    """
    global redis_client
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
