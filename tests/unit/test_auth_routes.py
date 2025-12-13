"""
Unit tests untuk Authentication routes
"""

import pytest
import json
from app.models import User

@pytest.mark.unit
class TestAuthRoutes:
    """Test suite untuk endpoint autentikasi"""
    
    def test_register_success(self, client, db_session):
        """Test registrasi user berhasil"""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123!",
            "role": "Operator"
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['user']['username'] == 'newuser'
        
        # Verifikasi di DB
        user = db_session.query(User).filter_by(username='newuser').first()
        assert user is not None
    
    def test_register_duplicate(self, client, db_session):
        """Test registrasi dengan username yang sudah ada"""
        # Buat user awal
        existing_user = User(
            username='existing',
            email='existing@example.com',
            role='Operator'
        )
        existing_user.set_password('Password123!')
        db_session.add(existing_user)
        db_session.commit()
        
        payload = {
            "username": "existing",
            "email": "other@example.com",
            "password": "Password123!",
            "role": "Operator"
        }
        
        response = client.post(
            '/api/v1/auth/register',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['message']
    
    def test_login_success(self, client, db_session):
        """Test login berhasil"""
        # Setup user
        user = User(username='loginuser', email='login@example.com', role='Operator')
        user.set_password('Password123!')
        db_session.add(user)
        db_session.commit()
        
        payload = {
            "username": "loginuser",
            "password": "Password123!"
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'refresh_token' in data
    
    def test_login_failure(self, client, db_session):
        """Test login gagal (wrong password)"""
        # Setup user
        user = User(username='failuser', email='fail@example.com', role='Operator')
        user.set_password('Password123!')
        db_session.add(user)
        db_session.commit()
        
        payload = {
            "username": "failuser",
            "password": "WrongPassword!"
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_get_me_protected(self, client):
        """Test akses endpoint protected tanpa token"""
        response = client.get('/api/v1/auth/me')
        assert response.status_code == 401
    
    def test_get_me_success(self, client, db_session):
        """Test akses endpoint protected dengan token valid"""
        # Setup user & login untuk dapat token
        user = User(username='meuser', email='me@example.com', role='Operator')
        user.set_password('Password123!')
        db_session.add(user)
        db_session.commit()
        
        login_res = client.post(
            '/api/v1/auth/login',
            data=json.dumps({"username": "meuser", "password": "Password123!"}),
            content_type='application/json'
        )
        token = json.loads(login_res.data)['access_token']
        
        # Access protected route
        response = client.get(
            '/api/v1/auth/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == 'meuser'
