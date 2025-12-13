"""
Database package initialization
Exports database connection handlers for PostgreSQL and InfluxDB
"""

from app.database.postgres import (
    init_postgres_db,
    get_db,
    get_db_session,
    close_db_connection,
    Base
)

from app.database.influxdb import (
    init_influxdb,
    get_influxdb_client,
    write_sensor_data,
    query_sensor_data,
    close_influxdb_connection
)

from app.database.redis import (
    init_redis, 
    get_redis_client,
    blacklist_token,
    is_token_blacklisted
)

__all__ = [
    # PostgreSQL
    'init_postgres_db',
    'get_db',
    'get_db_session',
    'close_db_connection',
    'Base',
    
    # InfluxDB
    'init_influxdb',
    'get_influxdb_client',
    'write_sensor_data',
    'query_sensor_data',
    'close_influxdb_connection',
    
    # Redis
    'init_redis',
    'get_redis_client',
    'blacklist_token',
    'is_token_blacklisted'
]
