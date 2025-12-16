"""
Unit tests untuk Configuration routes
"""

import json

import pytest

from app.models import User


@pytest.mark.unit
class TestConfigRoutes:
    """Test suite untuk endpoint konfigurasi"""

    @pytest.fixture
    def operator_token(self, client, db_session, unique_username):
        """Fixture untuk mendapatkan token role Operator"""
        user = User(username=unique_username, email=f"{unique_username}@example.com", role="Operator")
        user.set_password("Password123!")
        db_session.add(user)
        db_session.commit()

        res = client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": unique_username, "password": "Password123!"}),
            content_type="application/json",
        )
        return json.loads(res.data)["access_token"]

    @pytest.fixture
    def management_token(self, client, db_session):
        """Fixture untuk mendapatkan token role Management"""
        # Use a hardcoded but unique enough username with timestamp
        import time

        mgmt_username = f"mgmt_user_{int(time.time() * 1000) % 100000}"
        user = User(username=mgmt_username, email=f"{mgmt_username}@example.com", role="Management")
        user.set_password("Password123!")
        db_session.add(user)
        db_session.commit()

        res = client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": mgmt_username, "password": "Password123!"}),
            content_type="application/json",
        )
        return json.loads(res.data)["access_token"]

    def test_get_config_authorized(self, client, management_token):
        """Test ambil config dengan permission read:config (Management)"""
        response = client.get("/api/v1/config", headers={"Authorization": f"Bearer {management_token}"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "config" in data

    def test_update_config_unauthorized_role(self, client, operator_token):
        """Test update config dengan role tidak cukup (Operator)"""
        payload = {"setting_name": "max_temp", "setting_value": "100"}

        response = client.post(
            "/api/v1/config/update",
            headers={"Authorization": f"Bearer {operator_token}"},
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Operator tidak punya write:config, harusnya 403
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_update_config_authorized_role(self, client, management_token):
        """Test update config dengan role Management"""
        payload = {"setting_name": "max_temp", "setting_value": "100"}

        response = client.post(
            "/api/v1/config/update",
            headers={"Authorization": f"Bearer {management_token}"},
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
