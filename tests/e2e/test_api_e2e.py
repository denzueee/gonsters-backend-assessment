"""
End-to-end tests for API endpoints
"""

import pytest
import json
from datetime import datetime, timedelta
from uuid import uuid4

from app.models import MachineMetadata


@pytest.mark.e2e
class TestIngestEndpointE2E:
    """End-to-end tests for ingestion endpoint"""
    
    def test_successful_ingestion_single_machine(self, client, sample_machine):
        """Test successful ingestion for single machine"""
        payload = {
            "gateway_id": "e2e-gateway-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": str(sample_machine.id),
                    "sensor_type": sample_machine.sensor_type,
                    "location": sample_machine.location,
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
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['summary']['total_machines'] == 1
        assert data['summary']['total_readings'] == 1
        assert len(data['details']) == 1
        assert data['details'][0]['status'] == 'success'
    
    def test_successful_ingestion_multiple_machines(self, client, sample_machines):
        """Test successful ingestion for multiple machines"""
        batch = []
        for machine in sample_machines[:3]:  # Use first 3 machines
            batch.append({
                "machine_id": str(machine.id),
                "sensor_type": machine.sensor_type,
                "location": machine.location,
                "readings": [
                    {
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "temperature": 70.0 + len(batch),
                        "pressure": 100.0 + len(batch)
                    }
                ]
            })
        
        payload = {
            "gateway_id": "e2e-gateway-002",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": batch
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['summary']['total_machines'] == 3
        assert len(data['details']) == 3
    
    def test_ingestion_with_multiple_readings(self, client, sample_machine):
        """Test ingestion with multiple readings per machine"""
        readings = []
        for i in range(5):
            readings.append({
                "timestamp": (datetime.utcnow() - timedelta(seconds=i*10)).isoformat() + "Z",
                "temperature": 70.0 + i,
                "pressure": 100.0 + i * 0.5
            })
        
        payload = {
            "gateway_id": "e2e-gateway-003",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": str(sample_machine.id),
                    "sensor_type": sample_machine.sensor_type,
                    "location": sample_machine.location,
                    "readings": readings
                }
            ]
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['summary']['total_readings'] == 5
    
    def test_ingestion_machine_not_found(self, client):
        """Test ingestion with non-existent machine"""
        fake_uuid = str(uuid4())
        
        payload = {
            "gateway_id": "e2e-gateway-004",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": fake_uuid,
                    "sensor_type": "Temperature",
                    "location": "Test Floor",
                    "readings": [
                        {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "temperature": 72.5
                        }
                    ]
                }
            ]
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'errors' in data
    
    def test_partial_success_ingestion(self, client, sample_machine):
        """Test partial success when some machines fail"""
        fake_uuid = str(uuid4())
        
        payload = {
            "gateway_id": "e2e-gateway-005",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": str(sample_machine.id),
                    "sensor_type": sample_machine.sensor_type,
                    "location": sample_machine.location,
                    "readings": [
                        {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "temperature": 72.5
                        }
                    ]
                },
                {
                    "machine_id": fake_uuid,
                    "sensor_type": "Temperature",
                    "location": "Test Floor",
                    "readings": [
                        {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "temperature": 73.0
                        }
                    ]
                }
            ]
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return 207 Multi-Status for partial success
        assert response.status_code in [207, 400]
        data = json.loads(response.data)
        assert 'errors' in data or 'details' in data


@pytest.mark.e2e
class TestRetrievalEndpointE2E:
    """End-to-end tests for retrieval endpoint"""
    
    def test_successful_retrieval(self, client, app, sample_machine):
        """Test successful data retrieval"""
        # Extract machine ID early to avoid detached instance issues
        machine_id = str(sample_machine.id)
        sensor_type = sample_machine.sensor_type
        location = sample_machine.location
        
        # First, ingest some data
        with app.app_context():
            from app.database import write_sensor_data
            
            for i in range(3):
                write_sensor_data(
                    machine_id=machine_id,
                    sensor_type=sensor_type,
                    location=location,
                    temperature=70.0 + i,
                    timestamp=datetime.utcnow() - timedelta(minutes=i*10)
                )
        
        # Retrieve data
        response = client.get(
            f'/api/v1/data/machine/{machine_id}',
            query_string={
                'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
                'end_time': datetime.utcnow().isoformat() + 'Z',
                'interval': 'raw'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'machine' in data
        assert data['machine']['machine_id'] == machine_id
        assert 'data' in data
        assert 'pagination' in data
    
    def test_retrieval_with_aggregation(self, client, app, sample_machine):
        """Test retrieval with aggregation interval"""
        # Ingest data
        with app.app_context():
            from app.database import write_sensor_data
            
            for i in range(10):
                write_sensor_data(
                    machine_id=str(sample_machine.id),
                    sensor_type=sample_machine.sensor_type,
                    location=sample_machine.location,
                    temperature=70.0 + i,
                    timestamp=datetime.utcnow() - timedelta(minutes=i*6)
                )
        
        # Retrieve with hourly aggregation
        response = client.get(
            f'/api/v1/data/machine/{sample_machine.id}',
            query_string={
                'start_time': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                'interval': '1h'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['query']['interval'] == '1h'
    
    def test_retrieval_with_field_filtering(self, client, app, sample_machine):
        """Test retrieval with field filtering"""
        # Ingest data
        with app.app_context():
            from app.database import write_sensor_data
            
            write_sensor_data(
                machine_id=str(sample_machine.id),
                sensor_type=sample_machine.sensor_type,
                location=sample_machine.location,
                temperature=72.0,
                pressure=101.0,
                speed=1450.0
            )
        
        # Retrieve only temperature
        response = client.get(
            f'/api/v1/data/machine/{sample_machine.id}',
            query_string={
                'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
                'fields': 'temperature'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['query']['fields'] == ['temperature']
    
    def test_retrieval_with_pagination(self, client, app, sample_machine):
        """Test retrieval with pagination"""
        # Ingest multiple data points
        with app.app_context():
            from app.database import write_sensor_data
            
            for i in range(20):
                write_sensor_data(
                    machine_id=str(sample_machine.id),
                    sensor_type=sample_machine.sensor_type,
                    location=sample_machine.location,
                    temperature=70.0 + i,
                    timestamp=datetime.utcnow() - timedelta(minutes=i)
                )
        
        # Retrieve with limit
        response = client.get(
            f'/api/v1/data/machine/{sample_machine.id}',
            query_string={
                'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
                'limit': 10,
                'offset': 0
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pagination']['limit'] == 10
        assert data['pagination']['offset'] == 0


@pytest.mark.e2e
class TestCompleteWorkflow:
    """End-to-end tests for complete workflows"""
    
    def test_ingest_and_retrieve_workflow(self, client, sample_machine):
        """Test complete workflow: ingest data then retrieve it"""
        # Extract machine data early
        machine_id = str(sample_machine.id)
        sensor_type = sample_machine.sensor_type
        location = sample_machine.location
        
        # Step 1: Ingest data
        ingest_payload = {
            "gateway_id": "workflow-gateway-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": machine_id,
                    "sensor_type": sensor_type,
                    "location": location,
                    "readings": [
                        {
                            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z",
                            "temperature": 72.5,
                            "pressure": 101.3
                        },
                        {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "temperature": 73.0,
                            "pressure": 101.5
                        }
                    ]
                }
            ]
        }
        
        ingest_response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(ingest_payload),
            content_type='application/json'
        )
        
        assert ingest_response.status_code == 201
        
        # Step 2: Retrieve the ingested data
        retrieval_response = client.get(
            f'/api/v1/data/machine/{machine_id}',
            query_string={
                'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z',
                'interval': 'raw'
            }
        )
        
        assert retrieval_response.status_code == 200
        retrieval_data = json.loads(retrieval_response.data)
        assert retrieval_data['status'] == 'success'
    
    def test_multiple_gateways_workflow(self, client, sample_machines):
        """Test workflow with multiple gateways and machines"""
        # Extract machine data early to avoid detached instance issues
        machines_data = [
            {
                'id': str(machine.id),
                'sensor_type': machine.sensor_type,
                'location': machine.location
            }
            for machine in sample_machines[:3]
        ]
        
        # Gateway 1 sends data for machines 1-2
        gateway1_payload = {
            "gateway_id": "workflow-gateway-001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": machines_data[0]['id'],
                    "sensor_type": machines_data[0]['sensor_type'],
                    "location": machines_data[0]['location'],
                    "readings": [{"timestamp": datetime.utcnow().isoformat() + "Z", "temperature": 71.0}]
                },
                {
                    "machine_id": machines_data[1]['id'],
                    "sensor_type": machines_data[1]['sensor_type'],
                    "location": machines_data[1]['location'],
                    "readings": [{"timestamp": datetime.utcnow().isoformat() + "Z", "pressure": 100.0}]
                }
            ]
        }
        
        response1 = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(gateway1_payload),
            content_type='application/json'
        )
        assert response1.status_code == 201
        
        # Gateway 2 sends data for machines 3-4
        gateway2_payload = {
            "gateway_id": "workflow-gateway-002",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": machines_data[2]['id'],
                    "sensor_type": machines_data[2]['sensor_type'],
                    "location": machines_data[2]['location'],
                    "readings": [{"timestamp": datetime.utcnow().isoformat() + "Z", "speed": 1500.0}]
                }
            ]
        }
        
        response2 = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(gateway2_payload),
            content_type='application/json'
        )
        assert response2.status_code == 201
        
        # Verify each machine's data can be retrieved
        for machine_data in machines_data:
            retrieval_response = client.get(
                f'/api/v1/data/machine/{machine_data["id"]}',
                query_string={
                    'start_time': (datetime.utcnow() - timedelta(hours=1)).isoformat() + 'Z'
                }
            )
            assert retrieval_response.status_code == 200
