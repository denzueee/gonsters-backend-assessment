"""
Modul Subscriber MQTT
Menangani koneksi dan pemrosesan pesan dari broker MQTT
"""

import json
import logging
from datetime import datetime

import paho.mqtt.client as mqtt

from app.config import get_config
from app.database import get_db, write_sensor_data
from app.models import MachineMetadata

logger = logging.getLogger(__name__)
config = get_config()


class MQTTSubscriber:
    """Implementasi MQTT Subscriber untuk penerimaan data sensor"""

    def __init__(self):
        self.client = None
        self.is_connected = False
        self.message_count = 0

    def on_connect(self, client, userdata, flags, rc):
        """Callback saat terhubung ke broker"""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            self.is_connected = True

            # Subscribe ke topic
            client.subscribe(config.MQTT_TOPIC, qos=config.MQTT_QOS)
            logger.info(f"Subscribed to topic: {config.MQTT_TOPIC}")
        else:
            logger.error(f"Connection failed with code: {rc}")
            self.is_connected = False

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback saat subscription dikonfirmasi"""
        logger.info(f"Subscription confirmed with QoS: {granted_qos}")

    def on_message(self, client, userdata, msg):  # noqa: C901
        """Callback saat menerima pesan baru"""
        try:
            topic = msg.topic
            payload = msg.payload.decode("utf-8")

            logger.debug(f"Received message on topic: {topic}")

            # Parse topic untuk mendapatkan machine ID
            # Format: factory/{factory_id}/machine/{machine_id}/telemetry
            topic_parts = topic.split("/")

            if len(topic_parts) != 5:
                logger.warning(f"Invalid topic format: {topic}")
                return

            machine_id = topic_parts[3]

            # Parse JSON
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON payload: {e}")
                return

            # Validasi field yang wajib ada
            required_fields = ["timestamp", "sensor_type"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"Missing required field: {field}")
                    return

            # Ambil data sensor
            timestamp_str = data.get("timestamp")
            sensor_type = data.get("sensor_type")
            temperature = data.get("temperature")
            pressure = data.get("pressure")
            speed = data.get("speed")

            # Minimal harus ada 1 nilai sensor
            if temperature is None and pressure is None and speed is None:
                logger.error("No sensor values in payload")
                return

            # Parse timestamp
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                logger.error(f"Invalid timestamp format: {timestamp_str}")
                return

            # Cek apakah machine ada di database
            with get_db() as db:
                machine = db.query(MachineMetadata).filter(MachineMetadata.id == machine_id).first()

                if not machine:
                    logger.error(f"Machine {machine_id} not found in database")
                    return

                location = machine.location

            # Simpan ke InfluxDB
            success = write_sensor_data(
                machine_id=machine_id,
                sensor_type=sensor_type,
                location=location,
                temperature=temperature,
                pressure=pressure,
                speed=speed,
                timestamp=timestamp,
            )

            if success:
                self.message_count += 1
                logger.info(
                    f"Data stored successfully for machine {machine_id} " f"(total messages: {self.message_count})"
                )

                # Broadcast ke WebSocket clients
                try:
                    from app.websocket.websocket_handler import broadcast_sensor_data

                    broadcast_sensor_data(
                        machine_id,
                        {
                            "machine_id": machine_id,
                            "sensor_type": sensor_type,
                            "location": location,
                            "timestamp": timestamp.isoformat() + "Z",
                            "temperature": temperature,
                            "pressure": pressure,
                            "speed": speed,
                        },
                    )
                except Exception as e:
                    logger.warning(f"Failed to broadcast WebSocket data: {str(e)}")
            else:
                logger.error(f"Failed to store data for machine {machine_id}")

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def on_disconnect(self, client, userdata, rc):
        """Callback saat koneksi terputus"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection. Code: {rc}")
            logger.info("Attempting to reconnect...")

    def start(self):
        """Mulai MQTT subscriber"""
        logger.info("Starting MQTT subscriber...")

        # Buat client instance
        self.client = mqtt.Client(client_id=config.MQTT_CLIENT_ID, clean_session=True, protocol=mqtt.MQTTv311)

        # Set auth jika ada
        if config.MQTT_USERNAME and config.MQTT_PASSWORD:
            self.client.username_pw_set(username=config.MQTT_USERNAME, password=config.MQTT_PASSWORD)

        # Tetapkan callback
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        # Set pesan will (Last Will and Testament)
        self.client.will_set(
            topic="factory/backend/status",
            payload=json.dumps({"status": "offline", "timestamp": datetime.utcnow().isoformat()}),
            qos=1,
            retain=True,
        )

        try:
            # Connect ke broker
            logger.info(f"Connecting to broker: {config.MQTT_BROKER}:{config.MQTT_PORT}")
            self.client.connect(host=config.MQTT_BROKER, port=config.MQTT_PORT, keepalive=60)

            # Start loop di thread terpisah
            self.client.loop_start()
            logger.info("MQTT subscriber started successfully")

        except Exception as e:
            logger.error(f"Failed to start MQTT subscriber: {str(e)}")
            raise

    def stop(self):
        """Hentikan MQTT subscriber"""
        if self.client:
            logger.info("Stopping MQTT subscriber...")
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT subscriber stopped")


# Instance global
_mqtt_subscriber = None


def get_mqtt_subscriber():
    """Mengambil singleton instance MQTTSubscriber"""
    global _mqtt_subscriber
    if _mqtt_subscriber is None:
        _mqtt_subscriber = MQTTSubscriber()
    return _mqtt_subscriber


def start_mqtt_subscriber():
    """Helper untuk memulai subscriber"""
    subscriber = get_mqtt_subscriber()
    subscriber.start()
    return subscriber


def stop_mqtt_subscriber():
    """Helper untuk menghentikan subscriber"""
    global _mqtt_subscriber
    if _mqtt_subscriber:
        _mqtt_subscriber.stop()
        _mqtt_subscriber = None
