"""
Modul Middleware untuk Autentikasi dan Otorisasi
Mengelola decorator untuk proteksi endpoint dan RBAC
"""

import logging
from functools import wraps

from flask import g, jsonify, request

from app.auth.jwt_handler import verify_token
from app.database import get_db
from app.database.redis import is_token_blacklisted
from app.models import AuditLog, User

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator untuk memvalidasi JWT token dan autentikasi user

    Returns:
        function: Decorated function yang memerlukan autentikasi
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"status": "error", "message": "Missing authorization header"}), 401

        if not auth_header.startswith("Bearer "):
            return (
                jsonify(
                    {"status": "error", "message": "Invalid authorization header format. Expected: Bearer <token>"}
                ),
                401,
            )

        token = auth_header.split(" ")[1]
        payload = verify_token(token, token_type="access")

        if not payload:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

        # Check blacklist
        if is_token_blacklisted(token):
            return jsonify({"status": "error", "message": "Token has been revoked"}), 401

        user_id = payload.get("sub")

        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 401

            if not user.is_active:
                return jsonify({"status": "error", "message": "User account is inactive"}), 401

            # Expunge the user from the session to make it detached but accessible
            # This ensures the user object remains usable after the session closes
            db.expunge(user)
            g.current_user = user
            g.token_payload = payload

        return f(*args, **kwargs)

    return decorated_function


def require_permission(permission):
    """
    Decorator untuk memvalidasi permission user

    Args:
        permission: Permission yang dibutuhkan (contoh: 'read:machines')

    Returns:
        function: Decorated function yang memerlukan permission tertentu
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = g.get("current_user")

            if not user:
                return jsonify({"status": "error", "message": "Authentication required"}), 401

            if not user.has_permission(permission):
                log_audit(
                    user=user,
                    action="UNAUTHORIZED_ACCESS",
                    resource=request.path,
                    method=request.method,
                    status_code=403,
                )

                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Insufficient permissions. Required: {permission}",
                            "required_permission": permission,
                            "user_permissions": user.get_permissions(),
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_role(role):
    """
    Decorator untuk memvalidasi role user

    Args:
        role: Role yang dibutuhkan (contoh: 'Management')

    Returns:
        function: Decorated function yang memerlukan role tertentu
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = g.get("current_user")

            if not user:
                return jsonify({"status": "error", "message": "Authentication required"}), 401

            if user.role != role:
                log_audit(
                    user=user,
                    action="UNAUTHORIZED_ACCESS",
                    resource=request.path,
                    method=request.method,
                    status_code=403,
                )

                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Insufficient role. Required: {role}",
                            "required_role": role,
                            "user_role": user.role,
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_any_role(roles):
    """
    Decorator untuk memvalidasi user memiliki salah satu dari beberapa role

    Args:
        roles: List role yang diperbolehkan

    Returns:
        function: Decorated function yang memerlukan salah satu role
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = g.get("current_user")

            if not user:
                return jsonify({"status": "error", "message": "Authentication required"}), 401

            if user.role not in roles:
                log_audit(
                    user=user,
                    action="UNAUTHORIZED_ACCESS",
                    resource=request.path,
                    method=request.method,
                    status_code=403,
                )

                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f'Insufficient role. Required one of: {", ".join(roles)}',
                            "required_roles": roles,
                            "user_role": user.role,
                        }
                    ),
                    403,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def log_audit(user, action, resource, method=None, status_code=None):
    """
    Mencatat aktivitas user ke audit log

    Args:
        user: Instance User model
        action: Aksi yang dilakukan
        resource: Resource yang diakses
        method: HTTP method (optional)
        status_code: HTTP status code (optional)
    """
    try:
        with get_db() as db:
            audit_log = AuditLog(
                user_id=user.id,
                username=user.username,
                role=user.role,
                action=action,
                resource=resource,
                method=method or request.method,
                status_code=str(status_code) if status_code else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )
            db.add(audit_log)
            db.commit()
    except Exception as e:
        logger.error(f"Failed to log audit: {str(e)}")


def log_successful_request():
    """
    Mencatat request yang berhasil ke audit log
    """
    user = g.get("current_user")
    if user:
        log_audit(
            user=user,
            action=request.endpoint or "UNKNOWN",
            resource=request.path,
            method=request.method,
            status_code=200,
        )
