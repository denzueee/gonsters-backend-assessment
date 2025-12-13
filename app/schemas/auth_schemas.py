"""
Pydantic schemas untuk autentikasi
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Alamat email")
    password: str = Field(..., min_length=8, max_length=100, description="Password")
    role: str = Field(default="Operator", description="Role user")
    factory_id: Optional[str] = Field(None, max_length=50, description="ID Factory")
    department: Optional[str] = Field(None, max_length=100, description="Departemen")

    @validator("role")
    def validate_role(cls, v):
        """Validasi role harus sesuai yang diperbolehkan"""
        allowed_roles = ["Operator", "Supervisor", "Management"]
        if v not in allowed_roles:
            raise ValueError(f'Role harus salah satu dari: {", ".join(allowed_roles)}')
        return v

    @validator("password")
    def validate_password(cls, v):
        """Validasi kekuatan password"""
        if len(v) < 8:
            raise ValueError("Password minimal 8 karakter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password harus mengandung minimal satu huruf kapital")
        if not any(c.islower() for c in v):
            raise ValueError("Password harus mengandung minimal satu huruf kecil")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password harus mengandung minimal satu angka")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john.doe",
                "email": "john.doe@factory.com",
                "password": "SecurePass123!",
                "role": "Operator",
                "factory_id": "factory-A",
                "department": "Production",
            }
        }


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username atau email")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {"example": {"username": "john.doe", "password": "SecurePass123!"}}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: dict

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "user": {
                    "id": "d1c2084b-f16a-4eea-89d9-4402095d3af5",
                    "username": "john.doe",
                    "email": "john.doe@factory.com",
                    "role": "Operator",
                },
            }
        }


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {"example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}}


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    factory_id: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    permissions: Optional[List[str]] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "d1c2084b-f16a-4eea-89d9-4402095d3af5",
                "username": "john.doe",
                "email": "john.doe@factory.com",
                "role": "Operator",
                "factory_id": "factory-A",
                "department": "Production",
                "is_active": True,
                "permissions": ["read:machines", "read:sensor_data"],
                "created_at": "2025-12-13T00:00:00Z",
            }
        }


class ConfigUpdateRequest(BaseModel):
    setting_name: str = Field(..., min_length=1, max_length=100, description="Nama setting")
    setting_value: str = Field(..., description="Nilai setting")

    class Config:
        json_schema_extra = {"example": {"setting_name": "max_temperature_threshold", "setting_value": "85.0"}}
