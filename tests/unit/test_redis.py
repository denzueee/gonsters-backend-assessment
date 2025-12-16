"""
Unit tests untuk Redis Handler
"""

from unittest.mock import MagicMock, patch

import pytest

from app.database.redis import get_redis_client, init_redis


@pytest.mark.unit
class TestRedisHandler:
    """Test suite untuk handler Redis"""

    @patch("redis.Redis")
    def test_init_redis_success(self, mock_redis):
        """Test inisialisasi Redis berhasil"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True

        client = init_redis()

        assert client is not None
        mock_client.ping.assert_called_once()

    @patch("redis.Redis")
    def test_init_redis_failure(self, mock_redis):
        """Test inisialisasi Redis gagal (ConnectionError)"""
        import redis

        mock_redis.side_effect = redis.ConnectionError("Connection refused")

        client = init_redis()

        assert client is None

    @patch("app.database.redis.init_redis")
    def test_get_redis_client_reconnect(self, mock_init):
        """Test reconnect jika client belum ada"""
        # Reset global client
        import app.database.redis

        app.database.redis.redis_client = None

        mock_client = MagicMock()
        mock_init.return_value = mock_client

        client = get_redis_client()

        assert client == mock_client
        mock_init.assert_called_once()
