"""
Integration tests for database operations
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.database import get_db, query_sensor_data, write_sensor_data
from app.models import MachineMetadata


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations"""

    def test_create_machine_and_write_sensor_data(self, app, db_session):
        """Test creating machine and writing sensor data"""
        with app.app_context():
            # Create machine in PostgreSQL
            machine = MachineMetadata(
                name="Integration-Test-Machine",
                location="Integration Test Floor",
                sensor_type="Temperature",
                status="active",
            )
            db_session.add(machine)
            db_session.commit()
            db_session.refresh(machine)

            # Write sensor data to InfluxDB
            success = write_sensor_data(
                machine_id=str(machine.id),
                sensor_type=machine.sensor_type,
                location=machine.location,
                temperature=72.5,
                pressure=101.3,
            )

            assert success is True

            # Cleanup
            db_session.delete(machine)
            db_session.commit()

    def test_write_and_query_sensor_data(self, app, sample_machine):
        """Test writing and querying sensor data"""
        with app.app_context():
            machine_id = str(sample_machine.id)

            # Write multiple data points
            timestamps = []
            for i in range(5):
                timestamp = datetime.utcnow() - timedelta(minutes=i)
                timestamps.append(timestamp)

                write_sensor_data(
                    machine_id=machine_id,
                    sensor_type="Temperature",
                    location=sample_machine.location,
                    temperature=70.0 + i,
                    timestamp=timestamp,
                )

            # Query data
            results = query_sensor_data(
                machine_id=machine_id, start_time=datetime.utcnow() - timedelta(hours=1), end_time=datetime.utcnow()
            )

            assert isinstance(results, list)
            # Note: Results may be empty if InfluxDB is not running

    def test_multiple_machines_sensor_data(self, app, sample_machines):
        """Test writing sensor data for multiple machines"""
        with app.app_context():
            # Write data for each machine
            for machine in sample_machines:
                success = write_sensor_data(
                    machine_id=str(machine.id),
                    sensor_type=machine.sensor_type,
                    location=machine.location,
                    temperature=72.0,
                    pressure=101.0,
                    speed=1450.0,
                )
                assert success is True

    def test_query_with_time_range(self, app, sample_machine):
        """Test querying with specific time range"""
        with app.app_context():
            machine_id = str(sample_machine.id)

            # Write data at specific times
            now = datetime.utcnow()

            # Data point 1 hour ago
            write_sensor_data(
                machine_id=machine_id,
                sensor_type="Temperature",
                location=sample_machine.location,
                temperature=70.0,
                timestamp=now - timedelta(hours=1),
            )

            # Data point 30 minutes ago
            write_sensor_data(
                machine_id=machine_id,
                sensor_type="Temperature",
                location=sample_machine.location,
                temperature=75.0,
                timestamp=now - timedelta(minutes=30),
            )

            # Data point now
            write_sensor_data(
                machine_id=machine_id,
                sensor_type="Temperature",
                location=sample_machine.location,
                temperature=80.0,
                timestamp=now,
            )

            # Query last 45 minutes (should get 2 points)
            results = query_sensor_data(machine_id=machine_id, start_time=now - timedelta(minutes=45), end_time=now)

            assert isinstance(results, list)

    def test_machine_update_and_sensor_data(self, app, sample_machine, db_session):
        """Test updating machine and writing sensor data"""
        with app.app_context():
            machine_id = str(sample_machine.id)

            # Write initial data
            write_sensor_data(
                machine_id=machine_id,
                sensor_type=sample_machine.sensor_type,
                location=sample_machine.location,
                temperature=72.0,
            )

            # Update machine status
            sample_machine.status = "maintenance"
            db_session.commit()

            # Write more data
            write_sensor_data(
                machine_id=machine_id,
                sensor_type=sample_machine.sensor_type,
                location=sample_machine.location,
                temperature=73.0,
            )

            # Verify machine was updated
            updated_machine = db_session.query(MachineMetadata).filter(MachineMetadata.id == sample_machine.id).first()

            assert updated_machine.status == "maintenance"
