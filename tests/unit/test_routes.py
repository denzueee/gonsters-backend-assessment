"""
Unit tests for API routes
"""

import pytest
import json
from datetime import datetime, timedelta
from uuid import uuid4

from app.models import MachineMetadata


@pytest.mark.unit
class TestHealthEndpoint:
    """Unit tests for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data


@pytest.mark.unit
class TestIngestEndpoint:
    """Unit tests for ingestion endpoint"""
    
    def test_ingest_missing_body(self, client):
        """Test ingestion with missing request body"""
        response = client.post(
            '/api/v1/data/ingest',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_ingest_invalid_json(self, client):
        """Test ingestion with invalid JSON"""
        response = client.post(
            '/api/v1/data/ingest',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 415]
    
    def test_ingest_missing_required_fields(self, client):
        """Test ingestion with missing required fields"""
        payload = {
            "gateway_id": "test-gateway"
            # Missing timestamp and batch
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'errors' in data or 'message' in data
    
    def test_ingest_empty_batch(self, client):
        """Test ingestion with empty batch"""
        payload = {
            "gateway_id": "test-gateway",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": []
        }
        
        response = client.post(
            '/api/v1/data/ingest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_ingest_invalid_machine_id(self, client):
        """Test ingestion with invalid machine ID"""
        payload = {
            "gateway_id": "test-gateway",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batch": [
                {
                    "machine_id": "invalid-uuid",
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


@pytest.mark.unit
class TestRetrievalEndpoint:
    """Unit tests for retrieval endpoint"""
    
    def test_retrieval_invalid_machine_id(self, client):
        """Test retrieval with invalid machine ID"""
        response = client.get('/api/v1/data/machine/invalid-uuid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_retrieval_machine_not_found(self, client):
        """Test retrieval with non-existent machine"""
        fake_uuid = str(uuid4())
        response = client.get(
            f'/api/v1/data/machine/{fake_uuid}',
            query_string={'start_time': datetime.utcnow().isoformat() + 'Z'}
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'not found' in data['message'].lower()
    
    def test_retrieval_missing_start_time(self, client, valid_machine_id):
        """Test retrieval without start_time parameter"""
        response = client.get(f'/api/v1/data/machine/{valid_machine_id}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'start_time' in str(data).lower()
    
    def test_retrieval_invalid_interval(self, client, valid_machine_id):
        """Test retrieval with invalid interval"""
        response = client.get(
            f'/api/v1/data/machine/{valid_machine_id}',
            query_string={
                'start_time': datetime.utcnow().isoformat() + 'Z',
                'interval': 'invalid_interval'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'interval' in str(data).lower()
    
    def test_retrieval_invalid_limit(self, client, valid_machine_id):
        """Test retrieval with invalid limit"""
        response = client.get(
            f'/api/v1/data/machine/{valid_machine_id}',
            query_string={
                'start_time': datetime.utcnow().isoformat() + 'Z',
                'limit': 'invalid'
            }
        )
        
        assert response.status_code == 400
    
    def test_retrieval_limit_out_of_range(self, client, valid_machine_id):
        """Test retrieval with limit out of range"""
        response = client.get(
            f'/api/v1/data/machine/{valid_machine_id}',
            query_string={
                'start_time': datetime.utcnow().isoformat() + 'Z',
                'limit': 20000  # Exceeds max 10000
            }
        )
        
        assert response.status_code == 400
