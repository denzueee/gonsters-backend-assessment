"""
Additional tests for data and auth routes to increase coverage
"""

import pytest
import json


@pytest.mark.unit
class TestDataRoutesAdditional:
    """Additional data routes tests for coverage"""
    
    def test_get_machine_data_invalid_machine_id(self, client):
        """Test get machine data with invalid UUID"""
        response = client.get('/api/v1/data/machine/invalid-uuid')
        
        # Should return error for invalid UUID
        assert response.status_code in [400, 404, 500]


@pytest.mark.unit  
class TestAuthRoutesAdditional:
    """Additional auth routes tests for coverage"""
    
    def test_register_missing_fields(self, client):
        """Test register with missing required fields"""
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps({"username": "test"}),  # Missing email, password
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_register_duplicate_username(self, client, db_session):
        """Test register with duplicate username"""
        from app.models import User
        
        # Create first user
        user = User(username='duplicate', email='first@example.com', role='Operator')
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        # Try to register with same username
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps({
                "username": "duplicate",
                "email": "second@example.com",
                "password": "Pass123!",
                "role": "Operator"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'exists' in data['message'].lower() or 'already' in data['message'].lower()
    
    def test_login_wrong_password(self, client, db_session):
        """Test login with wrong password"""
        from app.models import User
        
        user = User(username='testlogin', email='testlogin@example.com', role='Operator')
        user.set_password('CorrectPass123!')
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                "username": "testlogin",
                "password": "WrongPassword!"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'invalid' in data['message'].lower()
    
    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user"""
        from app.models import User
        
        user = User(username='inactive', email='inactive@example.com', role='Operator', is_active=False)
        user.set_password('Pass123!')
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                "username": "inactive",
                "password": "Pass123!"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'inactive' in data['message'].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps({
                "username": "doesnotexist",
                "password": "Pass123!"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
