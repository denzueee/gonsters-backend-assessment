"""
Additional tests for config routes error handling
"""

import json

import pytest

from app.models import User


@pytest.mark.unit
class TestConfigRoutesErrorHandling:
    """Test error handling in config routes"""

    @pytest.fixture
    def admin_user(self, db_session, unique_username):
        """Create an admin user for testing"""
        user = User(username=unique_username, email=f"{unique_username}@example.com", role="Management")
        user.set_password("AdminPass123!")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def admin_token(self, client, admin_user):
        """Get admin token"""
        res = client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": admin_user.username, "password": "AdminPass123!"}),
            content_type="application/json",
        )
        return json.loads(res.data)["access_token"]

    def test_update_config_invalid_data(self, client, admin_token):
        """Test update config with invalid data"""
        response = client.post(
            "/api/v1/config/update",
            headers={"Authorization": f"Bearer {admin_token}"},
            data=json.dumps({"invalid": "data"}),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_update_config_success(self, client, admin_token):
        """Test successful config update"""
        response = client.post(
            "/api/v1/config/update",
            headers={"Authorization": f"Bearer {admin_token}"},
            data=json.dumps({"setting_name": "test_setting", "setting_value": "test_value"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert "updated_setting" in data
        assert data["updated_setting"]["name"] == "test_setting"
        assert data["updated_setting"]["new_value"] == "test_value"
