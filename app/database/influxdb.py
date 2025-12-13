from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta
import logging

from app.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

influx_client = None
write_api = None
query_api = None


def init_influxdb():
    """
    Inisialisasi koneksi ke InfluxDB
    
    Returns:
        InfluxDBClient: Client object untuk InfluxDB
    """
    global influx_client, write_api, query_api
    
    config = get_config()
    
    try:
        influx_client = InfluxDBClient(
            url=config.INFLUXDB_URL,
            token=config.INFLUXDB_TOKEN,
            org=config.INFLUXDB_ORG,
            timeout=30000
        )
        
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        query_api = influx_client.query_api()
        
        health = influx_client.health()
        if health.status == "pass":
            logger.info("InfluxDB connection established successfully")
        else:
            logger.warning(f"InfluxDB health check: {health.status}")
        
        setup_retention_policy()
        
        return influx_client
        
    except Exception as e:
        logger.error(f"Failed to connect to InfluxDB: {str(e)}")
        raise


def setup_retention_policy():
    """Mengatur kebijakan retensi data"""
    config = get_config()
    
    try:
        logger.info(f"Retention policy: {config.INFLUXDB_RETENTION_WEEKS} weeks")
    except Exception as e:
        logger.error(f"Failed to setup retention policy: {str(e)}")


def get_influxdb_client():
    """Mengambil instance InfluxDB client, inisialisasi jika belum ada"""
    if influx_client is None:
        init_influxdb()
    return influx_client


def write_sensor_data(machine_id, sensor_type, location, 
                     temperature=None, pressure=None, 
                     speed=None, timestamp=None):
    """
    Menulis data sensor ke InfluxDB
    
    Args:
        machine_id: ID mesin
        sensor_type: Tipe sensor
        location: Lokasi mesin
        temperature: Nilai temperatur (opsional)
        pressure: Nilai tekanan (opsional)
        speed: Nilai kecepatan (opsional)
        timestamp: Waktu pengambilan data (opsional)
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    
    global write_api
    
    if write_api is None:
        init_influxdb()
    
    config = get_config()
    
    try:
        point = Point("sensor_readings")
        
        # Tags untuk indexing yang efisien
        point.tag("machine_id", machine_id)
        point.tag("sensor_type", sensor_type)
        point.tag("location", location)
        
        # Fields untuk menyimpan nilai aktual
        if temperature is not None:
            point.field("temperature", float(temperature))
        if pressure is not None:
            point.field("pressure", float(pressure))
        if speed is not None:
            point.field("speed", float(speed))
        
        # Set timestamp
        if timestamp:
            point.time(timestamp, WritePrecision.NS)
        else:
            point.time(datetime.utcnow(), WritePrecision.NS)
        
        write_api.write(
            bucket=config.INFLUXDB_BUCKET,
            org=config.INFLUXDB_ORG,
            record=point
        )
        
        logger.debug(f"Sensor data written for machine {machine_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to write sensor data: {str(e)}")
        return False


def query_sensor_data(machine_id=None, sensor_type=None,
                     start_time=None, end_time=None,
                     aggregation_window=None):
    """
    Query data sensor dari InfluxDB dengan filter opsional
    
    Args:
        machine_id: Filter berdasarkan ID mesin
        sensor_type: Filter berdasarkan tipe sensor
        start_time: Waktu mulai (default: 7 hari lalu)
        end_time: Waktu akhir (default: sekarang)
        aggregation_window: Window untuk agregasi data (misal: '1h')
    
    Returns:
        list: Daftar record data sensor
    """
    
    global query_api
    
    if query_api is None:
        init_influxdb()
    
    config = get_config()
    
    # Default time range 7 hari terakhir
    if start_time is None:
        start_time = datetime.utcnow() - timedelta(days=7)
    if end_time is None:
        end_time = datetime.utcnow()
    
    try:
        # Build Flux query  
        # Format timestamps for Flux query (RFC3339 format)
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        query = f'''
        from(bucket: "{config.INFLUXDB_BUCKET}")
            |> range(start: {start_str}, stop: {end_str})
            |> filter(fn: (r) => r["_measurement"] == "sensor_readings")
        '''
        
        # Tambah filter jika ada
        if machine_id:
            query += f'|> filter(fn: (r) => r["machine_id"] == "{machine_id}")\n'
        if sensor_type:
            query += f'|> filter(fn: (r) => r["sensor_type"] == "{sensor_type}")\n'
        
        # Agregasi jika diperlukan
        if aggregation_window:
            query += f'''
            |> aggregateWindow(every: {aggregation_window}, fn: mean, createEmpty: false)
            '''
        
        result = query_api.query(org=config.INFLUXDB_ORG, query=query)
        
        # Parse hasil query
        records = []
        for table in result:
            for record in table.records:
                records.append({
                    'time': record.get_time(),
                    'machine_id': record.values.get('machine_id'),
                    'sensor_type': record.values.get('sensor_type'),
                    'location': record.values.get('location'),
                    'field': record.get_field(),
                    'value': record.get_value()
                })
        
        logger.debug(f"Query returned {len(records)} records")
        return records
        
    except Exception as e:
        logger.error(f"Failed to query sensor data: {str(e)}")
        return []


def close_influxdb_connection():
    """Menutup koneksi InfluxDB"""
    global influx_client, write_api, query_api
    
    if influx_client:
        influx_client.close()
        logger.info("InfluxDB connection closed")
        influx_client = None
        write_api = None
        query_api = None
