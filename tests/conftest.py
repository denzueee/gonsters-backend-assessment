"""
Konfigurasi dan fixtures Pytest
"""

import pytest
import os
import sys
import random
from datetime import datetime
from uuid import uuid4

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import init_postgres_db, Base, get_db
from app.models import MachineMetadata
from app.config import TestingConfig
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope='session')
def app():
    """Membuat aplikasi Flask untuk testing"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    app.config.from_object(TestingConfig)
    
    with app.app_context():
        # Create tables
        engine = init_postgres_db()
        Base.metadata.create_all(engine)
        
        # Setup InfluxDB test bucket
        setup_influxdb_test_bucket()
        
        yield app
        
        # Cleanup
        Base.metadata.drop_all(engine)


def setup_influxdb_test_bucket():
    """Create test bucket in InfluxDB"""
    try:
        from app.database.influxdb import get_influxdb_client
        
        client = get_influxdb_client()
        buckets_api = client.buckets_api()
        
        # Try to find existing test bucket
        bucket_name = 'test_sensor_data'
        buckets = buckets_api.find_buckets().buckets
        test_bucket_exists = any(b.name == bucket_name for b in buckets)
        
        if not test_bucket_exists:
            # Create test bucket with 1 hour retention for tests
            buckets_api.create_bucket(
                bucket_name=bucket_name,
                org='gonsters',
                retention_rules=[{
                    "type": "expire",
                    "everySeconds": 3600  # 1 hour
                }]
            )
            logger.info(f"Created InfluxDB test bucket: {bucket_name}")
        else:
            logger.info(f"InfluxDB test bucket already exists: {bucket_name}")
            
    except Exception as e:
        logger.warning(f"InfluxDB test bucket setup skipped: {e}")
        logger.warning("InfluxDB-dependent tests may fail")


@pytest.fixture(scope='function')
def client(app):
    """Membuat test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Membuat session database untuk testing"""
    with app.app_context():
        with get_db() as session:
            yield session


@pytest.fixture(scope='function')
def sample_machine(db_session):
    """Membuat sample mesin untuk testing"""
    machine = MachineMetadata(
        name='Test-Machine-01',
        location='Test Floor 1',
        sensor_type='Temperature',
        status='active'
    )
    db_session.add(machine)
    db_session.commit()
    db_session.refresh(machine)
    
    yield machine
    
    # Cleanup
    db_session.delete(machine)
    db_session.commit()


@pytest.fixture(scope='function')
def sample_machines(db_session):
    """Membuat beberapa sample mesin untuk testing"""
    machines = []
    for i in range(5):
        machine = MachineMetadata(
            name=f'Test-Machine-{i+1:02d}',
            location=f'Test Floor {(i % 3) + 1}',
            sensor_type=['Temperature', 'Pressure', 'Speed'][i % 3],
            status=['active', 'inactive', 'maintenance'][i % 3]
        )
        db_session.add(machine)
        machines.append(machine)
    
    db_session.commit()
    for machine in machines:
        db_session.refresh(machine)
    
    yield machines
    
    # Cleanup
    for machine in machines:
        db_session.delete(machine)
    db_session.commit()


@pytest.fixture
def sample_ingest_payload():
    """Sample payload untuk endpoint ingestion"""
    return {
        "gateway_id": "test-gateway-001",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "batch": [
            {
                "machine_id": str(uuid4()),
                "sensor_type": "Temperature",
                "location": "Test Floor 1",
                "readings": [
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "temperature": 72.5,
                        "pressure": 101.3,
                        "speed": 1450.0
                    }
                ]
            }
        ]
    }


@pytest.fixture
def unique_username():
    """Generate unique username for tests"""
    return f"testuser_{random.randint(10000, 99999)}"


@pytest.fixture
def valid_machine_id(sample_machine):
    """Mengambil ID mesin yang valid untuk testing"""
    return str(sample_machine.id)


@pytest.fixture(scope='function')
def test_user(db_session):
    """Create a test user for authentication"""
    from app.models import User
    
    user = User(
        username='test_operator',
        email='test@example.com',
        role='Operator',
        factory_id='factory-test',
        department='Testing'
    )
    user.set_password('testpass123')
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    yield user
    
    # Cleanup
    db_session.delete(user)
    db_session.commit()


@pytest.fixture(scope='function')
def auth_token(app, test_user):
    """Generate JWT token for test user"""
    from app.auth import create_access_token
    
    with app.app_context():
        user_data = {
            'sub': str(test_user.id),
            'username': test_user.username,
            'email': test_user.email,
            'role': test_user.role,
            'permissions': test_user.get_permissions(),
            'factory_id': test_user.factory_id,
            'department': test_user.department
        }
        return create_access_token(user_data)


@pytest.fixture(scope='function')
def auth_headers(auth_token):
    """Generate authorization headers for API requests"""
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


# Pytest configuration
def pytest_configure(config):
    """Konfigurasi pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests"
    )
