"""
Unit tests for Pydantic schemas
"""

import pytest
from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from app.schemas import (
    SensorReading,
    MachineData,
    IngestRequest
)


@pytest.mark.unit
class TestSensorReading:
    """Unit tests for SensorReading schema"""
    
    def test_valid_sensor_reading(self):
        """Test valid sensor reading"""
        reading = SensorReading(
            timestamp=datetime.utcnow(),
            temperature=72.5,
            pressure=101.3,
            speed=1450.0
        )
        
        assert reading.temperature == 72.5
        assert reading.pressure == 101.3
        assert reading.speed == 1450.0
    
    def test_partial_sensor_reading(self):
        """Test sensor reading with only one field"""
        reading = SensorReading(
            timestamp=datetime.utcnow(),
            temperature=72.5
        )
        
        assert reading.temperature == 72.5
        assert reading.pressure is None
        assert reading.speed is None
    
    def test_invalid_temperature_range(self):
        """Test temperature out of valid range"""
        with pytest.raises(ValidationError) as exc_info:
            SensorReading(
                timestamp=datetime.utcnow(),
                temperature=-300.0  # Below absolute zero
            )
        
        assert 'temperature' in str(exc_info.value)
    
    def test_invalid_pressure_negative(self):
        """Test negative pressure"""
        with pytest.raises(ValidationError) as exc_info:
            SensorReading(
                timestamp=datetime.utcnow(),
                pressure=-10.0
            )
        
        assert 'pressure' in str(exc_info.value)
    
    def test_missing_timestamp(self):
        """Test missing timestamp"""
        with pytest.raises(ValidationError) as exc_info:
            SensorReading(temperature=72.5)
        
        assert 'timestamp' in str(exc_info.value)


@pytest.mark.unit
class TestMachineData:
    """Unit tests for MachineData schema"""
    
    def test_valid_machine_data(self):
        """Test valid machine data"""
        machine_data = MachineData(
            machine_id=uuid4(),
            sensor_type='Temperature',
            location='Test Floor',
            readings=[
                SensorReading(
                    timestamp=datetime.utcnow(),
                    temperature=72.5
                )
            ]
        )
        
        assert machine_data.sensor_type == 'Temperature'
        assert len(machine_data.readings) == 1
    
    def test_multiple_readings(self):
        """Test machine data with multiple readings"""
        machine_data = MachineData(
            machine_id=uuid4(),
            sensor_type='Temperature',
            location='Test Floor',
            readings=[
                SensorReading(timestamp=datetime.utcnow(), temperature=72.5),
                SensorReading(timestamp=datetime.utcnow(), temperature=73.0),
                SensorReading(timestamp=datetime.utcnow(), temperature=73.5)
            ]
        )
        
        assert len(machine_data.readings) == 3
    
    def test_empty_readings(self):
        """Test machine data with empty readings"""
        with pytest.raises(ValidationError) as exc_info:
            MachineData(
                machine_id=uuid4(),
                sensor_type='Temperature',
                location='Test Floor',
                readings=[]
            )
        
        assert 'readings' in str(exc_info.value)
    
    def test_invalid_machine_id(self):
        """Test invalid machine ID format"""
        with pytest.raises(ValidationError) as exc_info:
            MachineData(
                machine_id='invalid-uuid',
                sensor_type='Temperature',
                location='Test Floor',
                readings=[
                    SensorReading(timestamp=datetime.utcnow(), temperature=72.5)
                ]
            )
        
        assert 'machine_id' in str(exc_info.value)


@pytest.mark.unit
class TestIngestRequest:
    """Unit tests for IngestRequest schema"""
    
    def test_valid_ingest_request(self):
        """Test valid ingest request"""
        request = IngestRequest(
            gateway_id='gateway-001',
            timestamp=datetime.utcnow(),
            batch=[
                MachineData(
                    machine_id=uuid4(),
                    sensor_type='Temperature',
                    location='Test Floor',
                    readings=[
                        SensorReading(timestamp=datetime.utcnow(), temperature=72.5)
                    ]
                )
            ]
        )
        
        assert request.gateway_id == 'gateway-001'
        assert len(request.batch) == 1
    
    def test_multiple_machines_in_batch(self):
        """Test batch with multiple machines"""
        request = IngestRequest(
            gateway_id='gateway-001',
            timestamp=datetime.utcnow(),
            batch=[
                MachineData(
                    machine_id=uuid4(),
                    sensor_type='Temperature',
                    location='Floor 1',
                    readings=[SensorReading(timestamp=datetime.utcnow(), temperature=72.5)]
                ),
                MachineData(
                    machine_id=uuid4(),
                    sensor_type='Pressure',
                    location='Floor 2',
                    readings=[SensorReading(timestamp=datetime.utcnow(), pressure=101.3)]
                )
            ]
        )
        
        assert len(request.batch) == 2
    
    def test_empty_batch(self):
        """Test empty batch"""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(
                gateway_id='gateway-001',
                timestamp=datetime.utcnow(),
                batch=[]
            )
        
        assert 'batch' in str(exc_info.value)
    
    def test_batch_too_large(self):
        """Test batch exceeding max size"""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(
                gateway_id='gateway-001',
                timestamp=datetime.utcnow(),
                batch=[
                    MachineData(
                        machine_id=uuid4(),
                        sensor_type='Temperature',
                        location='Floor 1',
                        readings=[SensorReading(timestamp=datetime.utcnow(), temperature=72.5)]
                    )
                    for _ in range(1001)  # Exceeds max_items=1000
                ]
            )
        
        assert 'batch' in str(exc_info.value)
    
    def test_missing_gateway_id(self):
        """Test missing gateway_id"""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(
                timestamp=datetime.utcnow(),
                batch=[
                    MachineData(
                        machine_id=uuid4(),
                        sensor_type='Temperature',
                        location='Floor 1',
                        readings=[SensorReading(timestamp=datetime.utcnow(), temperature=72.5)]
                    )
                ]
            )
        
        assert 'gateway_id' in str(exc_info.value)
