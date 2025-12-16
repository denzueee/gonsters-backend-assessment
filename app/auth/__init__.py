"""
Auth package initialization
"""

from app.auth.jwt_handler import create_access_token, create_refresh_token, decode_token, verify_token
from app.auth.middleware import (
    log_audit,
    log_successful_request,
    require_any_role,
    require_auth,
    require_permission,
    require_role,
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "require_auth",
    "require_permission",
    "require_role",
    "require_any_role",
    "log_audit",
    "log_successful_request",
]
