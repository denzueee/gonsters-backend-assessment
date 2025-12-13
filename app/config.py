"""
Modul konfigurasi untuk GONSTERS Backend Assessment
Menangani environment variables dan pengaturan koneksi database
"""

import os
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()


class Config:
    
    # Konfigurasi Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Konfigurasi PostgreSQL
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'gonsters_db')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    # URI Database SQLAlchemy
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Konfigurasi InfluxDB
    INFLUXDB_URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
    INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token')
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG', 'gonsters')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET', 'sensor_data')
    
    # Konfigurasi MQTT
    MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
    MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'factory/+/machine/+/telemetry')
    MQTT_QOS = int(os.getenv('MQTT_QOS', '1'))
    MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'gonsters-backend-001')
    
    # Konfigurasi Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Konfigurasi JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 1 jam
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', '2592000'))  # 30 hari
    
    # Konfigurasi Retensi Data
    # Default: 52 minggu (1 tahun) untuk raw data
    INFLUXDB_RETENTION_WEEKS = int(os.getenv('INFLUXDB_RETENTION_WEEKS', '52'))


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Override dengan setting yang lebih kuat untuk production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    
    # Gunakan database test terpisah
    POSTGRES_DB = 'gonsters_test_db'
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@"
        f"{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{POSTGRES_DB}"
    )
    
    # Konfigurasi InfluxDB untuk testing
    # Gunakan token dari INFLUXDB_INIT_ADMIN_TOKEN (set by Docker) atau fallback ke env
    INFLUXDB_TOKEN = os.getenv('INFLUXDB_INIT_ADMIN_TOKEN', os.getenv('INFLUXDB_TOKEN', 'my-super-secret-auth-token'))
    
    # Gunakan bucket test terpisah
    INFLUXDB_BUCKET = 'test_sensor_data'


# Dictionary konfigurasi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Mengambil konfigurasi berdasarkan environment variable"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
