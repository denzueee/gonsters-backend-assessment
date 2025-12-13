"""
Unit tests for database handlers
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.database import (
    init_postgres_db,
    init_influxdb,
    write_sensor_data,
    query_sensor_data
)
from app.models import MachineMetadata


@pytest.mark.unit
class TestPostgresHandler:
    """Unit tests for PostgreSQL handler"""
    
    def test_init_postgres_db(self, app):
        """Test PostgreSQL initialization"""
        with app.app_context():
            engine = init_postgres_db()
            assert engine is not None
            assert engine.url.database == 'gonsters_test_db'
    
    def test_create_machine(self, db_session):
        """Test creating a machine"""
        machine = MachineMetadata(
            name='Unit-Test-Machine',
            location='Unit Test Floor',
            sensor_type='Temperature',
            status='active'
        )
        db_session.add(machine)
        db_session.commit()
        
        assert machine.id is not None
        assert machine.name == 'Unit-Test-Machine'
        assert machine.status == 'active'
    
    def test_query_machine(self, sample_machine, db_session):
        """Test querying a machine"""
        machine = db_session.query(MachineMetadata).filter(
            MachineMetadata.id == sample_machine.id
        ).first()
        
        assert machine is not None
        assert machine.name == sample_machine.name
        assert machine.location == sample_machine.location
    
    def test_update_machine(self, sample_machine, db_session):
        """Test updating a machine"""
        sample_machine.status = 'maintenance'
        db_session.commit()
        
        updated = db_session.query(MachineMetadata).filter(
            MachineMetadata.id == sample_machine.id
        ).first()
        
        assert updated.status == 'maintenance'
    
    def test_machine_to_dict(self, sample_machine):
        """Test machine to_dict method"""
        data = sample_machine.to_dict()
        
        assert 'id' in data
        assert 'name' in data
        assert 'location' in data
        assert 'sensor_type' in data
        assert 'status' in data
        assert data['name'] == sample_machine.name
    
    def test_machine_status_constraint(self, db_session):
        """Test machine status CHECK constraint"""
        machine = MachineMetadata(
            name='Invalid-Status-Machine',
            location='Test Floor',
            sensor_type='Temperature',
            status='invalid_status'  # Invalid status
        )
        db_session.add(machine)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
        
        db_session.rollback()


@pytest.mark.unit
class TestInfluxDBHandler:
    """Unit tests for InfluxDB handler"""
    
    def test_init_influxdb(self, app):
        """Test InfluxDB initialization"""
        with app.app_context():
            client = init_influxdb()
            assert client is not None
    
    def test_write_sensor_data(self, app, valid_machine_id):
        """Test writing sensor data"""
        with app.app_context():
            success = write_sensor_data(
                machine_id=valid_machine_id,
                sensor_type='Temperature',
                location='Test Floor',
                temperature=72.5,
                pressure=101.3,
                speed=1450.0
            )
            
            assert success is True
    
    def test_write_sensor_data_partial_fields(self, app, valid_machine_id):
        """Test writing sensor data with partial fields"""
        with app.app_context():
            # Only temperature
            success = write_sensor_data(
                machine_id=valid_machine_id,
                sensor_type='Temperature',
                location='Test Floor',
                temperature=72.5
            )
            assert success is True
            
            # Only pressure
            success = write_sensor_data(
                machine_id=valid_machine_id,
                sensor_type='Pressure',
                location='Test Floor',
                pressure=101.3
            )
            assert success is True
    
    def test_query_sensor_data(self, app, valid_machine_id):
        """Test querying sensor data"""
        with app.app_context():
            # Write test data
            write_sensor_data(
                machine_id=valid_machine_id,
                sensor_type='Temperature',
                location='Test Floor',
                temperature=72.5,
                timestamp=datetime.utcnow()
            )
            
            # Query data
            results = query_sensor_data(
                machine_id=valid_machine_id,
                start_time=datetime.utcnow() - timedelta(hours=1),
                end_time=datetime.utcnow()
            )
            
            assert isinstance(results, list)
    
    def test_query_with_aggregation(self, app, valid_machine_id):
        """Test querying with aggregation window"""
        with app.app_context():
            # Write multiple data points
            for i in range(5):
                write_sensor_data(
                    machine_id=valid_machine_id,
                    sensor_type='Temperature',
                    location='Test Floor',
                    temperature=70.0 + i,
                    timestamp=datetime.utcnow() - timedelta(minutes=i)
                )
            
            # Query with aggregation
            results = query_sensor_data(
                machine_id=valid_machine_id,
                start_time=datetime.utcnow() - timedelta(hours=1),
                end_time=datetime.utcnow(),
                aggregation_window='1h'
            )
            
            assert isinstance(results, list)
