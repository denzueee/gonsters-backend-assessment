"""
Unit tests untuk MQTT Subscriber
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.mqtt.mqtt_subscriber import MQTTSubscriber


@pytest.mark.unit
class TestMQTTSubscriber:
    """Test untuk kelas MQTTSubscriber"""

    @pytest.fixture
    def subscriber(self):
        """Fixture untuk membuat instance subscriber"""
        return MQTTSubscriber()

    @pytest.fixture
    def mock_client(self):
        """Mock MQTT client"""
        client = MagicMock()
        return client

    def test_init(self, subscriber):
        """Test inisialisasi subscriber"""
        assert subscriber.client is None
        assert subscriber.is_connected is False
        assert subscriber.message_count == 0

    def test_on_connect_success(self, subscriber):
        """Test callback on_connect berhasil"""
        client = MagicMock()
        subscriber.on_connect(client, None, None, 0)

        assert subscriber.is_connected is True
        client.subscribe.assert_called_once()

    def test_on_connect_failure(self, subscriber):
        """Test callback on_connect gagal"""
        client = MagicMock()
        subscriber.on_connect(client, None, None, 1)  # rc != 0

        assert subscriber.is_connected is False
        client.subscribe.assert_not_called()

    @patch("app.mqtt.mqtt_subscriber.get_db")
    @patch("app.mqtt.mqtt_subscriber.write_sensor_data")
    def test_on_message_success(self, mock_write, mock_get_db, subscriber):
        """Test pemrosesan pesan yang valid"""
        # Mock database session dan machine query
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        mock_machine = MagicMock()
        mock_machine.location = "Test Location"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_machine

        mock_write.return_value = True

        # Buat pesan dummy
        msg = MagicMock()
        msg.topic = "factory/F1/machine/M1/telemetry"
        msg.payload = json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "sensor_type": "Temperature",
                "temperature": 75.5,
                "pressure": 101.2,
                "speed": 1000,
            }
        ).encode("utf-8")

        # Panggil on_message
        subscriber.on_message(None, None, msg)

        # Verifikasi
        mock_write.assert_called_once()
        assert subscriber.message_count == 1

    @patch("app.mqtt.mqtt_subscriber.write_sensor_data")
    def test_on_message_invalid_topic(self, mock_write, subscriber):
        """Test pesan dengan topic format salah"""
        msg = MagicMock()
        msg.topic = "invalid/topic/format"  # Salah format
        msg.payload = b"{}"

        subscriber.on_message(None, None, msg)

        mock_write.assert_not_called()

    @patch("app.mqtt.mqtt_subscriber.write_sensor_data")
    def test_on_message_invalid_json(self, mock_write, subscriber):
        """Test pesan dengan JSON invalid"""
        msg = MagicMock()
        msg.topic = "factory/F1/machine/M1/telemetry"
        msg.payload = b"not a json"

        subscriber.on_message(None, None, msg)

        mock_write.assert_not_called()

    @patch("app.mqtt.mqtt_subscriber.write_sensor_data")
    def test_on_message_missing_fields(self, mock_write, subscriber):
        """Test pesan dengan field yang hilang"""
        msg = MagicMock()
        msg.topic = "factory/F1/machine/M1/telemetry"
        # Missing sensor_type
        msg.payload = json.dumps({"timestamp": datetime.utcnow().isoformat() + "Z"}).encode("utf-8")

        subscriber.on_message(None, None, msg)

        mock_write.assert_not_called()
