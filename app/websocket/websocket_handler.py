"""
WebSocket Handler dengan Flask-SocketIO
Menangani real-time communication dengan frontend
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

# Initialize SocketIO dengan CORS
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')


@socketio.on('connect')
def handle_connect():
    """Handler saat client connect"""
    token = request.args.get('token')
    if not token:
        logger.warning("WebSocket connection rejected: No token provided")
        return False
    
    # TODO: Validate JWT token if needed
    logger.info(f"WebSocket client connected")
    emit('connected', {'status': 'success', 'message': 'Connected to GONSTERS real-time server'})
    return True


@socketio.on('disconnect')
def handle_disconnect():
    """Handler saat client disconnect"""
    logger.info("WebSocket client disconnected")


@socketio.on('subscribe_machine')
def handle_subscribe_machine(data):
    """Subscribe ke updates mesin tertentu"""
    machine_id = data.get('machine_id')
    if machine_id:
        room_name = f"machine_{machine_id}"
        join_room(room_name)
        emit('subscribed', {'machine_id': machine_id, 'room': room_name})
        logger.info(f"Client subscribed to machine: {machine_id}")


@socketio.on('unsubscribe_machine')
def handle_unsubscribe_machine(data):
    """Unsubscribe dari updates mesin"""
    machine_id = data.get('machine_id')
    if machine_id:
        room_name = f"machine_{machine_id}"
        leave_room(room_name)
        emit('unsubscribed', {'machine_id': machine_id})
        logger.info(f"Client unsubscribed from machine: {machine_id}")


@socketio.on('subscribe_all')
def handle_subscribe_all():
    """Subscribe ke semua updates"""
    join_room('all_machines')
    emit('subscribed_all', {'status': 'success'})
    logger.info("Client subscribed to all machines")


def broadcast_sensor_data(machine_id, sensor_data):
    """
    Broadcast data sensor ke semua client yang subscribe
    Dipanggil dari mqtt_subscriber setelah data disimpan
    
    Args:
        machine_id: ID mesin
        sensor_data: Dict berisi data sensor (temperature, pressure, speed, timestamp, dll)
    """
    try:
        # Broadcast ke room spesifik machine
        socketio.emit('sensor_data', sensor_data, room=f"machine_{machine_id}")
        
        # Broadcast ke room all_machines
        socketio.emit('sensor_data', sensor_data, room='all_machines')
        
        logger.debug(f"Broadcasted sensor data for machine {machine_id}")
    except Exception as e:
        logger.error(f"Error broadcasting sensor data: {str(e)}")


def broadcast_alert(alert_data):
    """
    Broadcast alert ke semua client
    
    Args:
        alert_data: Dict berisi data alert
    """
    try:
        # Broadcast ke semua connected clients (room 'all_machines')
        socketio.emit('alert', alert_data, room='all_machines')
        logger.info(f"Broadcasted alert: {alert_data.get('message', 'Unknown')}")
    except Exception as e:
        logger.error(f"Error broadcasting alert: {str(e)}")
