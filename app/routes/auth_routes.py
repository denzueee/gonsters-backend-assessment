"""
Authentication routes
Handles user registration, login, token refresh, and logout
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from datetime import datetime
import logging

from app.database import get_db, blacklist_token
from app.models import User
from app.schemas import RegisterRequest, LoginRequest, RefreshTokenRequest
from app.auth import create_access_token, create_refresh_token, verify_token, require_auth, log_audit
from app.config import get_config

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
logger = logging.getLogger(__name__)
config = get_config()


@bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/v1/auth/register
    Mendaftarkan user baru

    Request Body:
        {
            "username": "john.doe",
            "email": "john.doe@factory.com",
            "password": "SecurePass123!",
            "role": "Operator",
            "factory_id": "factory-A",
            "department": "Production"
        }

    Returns:
        201: User berhasil dibuat
        400: Error validasi atau user sudah ada
    """
    try:
        # Validasi request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body is required"}), 400

        try:
            register_request = RegisterRequest(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({"field": ".".join(str(loc) for loc in error["loc"]), "error": error["msg"]})

            return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

        # Cek user yang sudah ada
        with get_db() as db:
            existing_user = (
                db.query(User)
                .filter((User.username == register_request.username) | (User.email == register_request.email))
                .first()
            )

            if existing_user:
                return jsonify({"status": "error", "message": "User with this username or email already exists"}), 400

            # Buat user baru
            user = User(
                username=register_request.username,
                email=register_request.email,
                role=register_request.role,
                factory_id=register_request.factory_id,
                department=register_request.department,
            )
            user.set_password(register_request.password)

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"New user registered: {user.username} ({user.role})")

            return (
                jsonify({"status": "success", "message": "User registered successfully", "user": user.to_dict()}),
                201,
            )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/v1/auth/login
    Autentikasi user dan mengembalikan JWT tokens

    Request Body:
        {
            "username": "john.doe",
            "password": "SecurePass123!"
        }

    Returns:
        200: Login berhasil dengan tokens
        401: Kredensial tidak valid
        400: Error validasi
    """
    try:
        # Validasi request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body is required"}), 400

        try:
            login_request = LoginRequest(**data)
        except ValidationError as e:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Validation failed",
                        "errors": [
                            {"field": ".".join(str(loc) for loc in err["loc"]), "error": err["msg"]}
                            for err in e.errors()
                        ],
                    }
                ),
                400,
            )

        # Cari user (username/email)
        with get_db() as db:
            user = (
                db.query(User)
                .filter((User.username == login_request.username) | (User.email == login_request.username))
                .first()
            )

            if not user or not user.check_password(login_request.password):
                return jsonify({"status": "error", "message": "Invalid username or password"}), 401

            if not user.is_active:
                return jsonify({"status": "error", "message": "User account is inactive"}), 401

            # Update waktu login
            user.last_login = datetime.utcnow()
            db.commit()

            # Buat token JWT
            user_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "permissions": user.get_permissions(),
                "factory_id": user.factory_id,
                "department": user.department,
            }

            access_token = create_access_token(user_data)
            refresh_token = create_refresh_token(str(user.id))

            logger.info(f"User logged in: {user.username}")

            return (
                jsonify(
                    {
                        "status": "success",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "Bearer",
                        "expires_in": config.JWT_ACCESS_TOKEN_EXPIRES,
                        "user": user.to_dict(include_permissions=True),
                    }
                ),
                200,
            )

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@bp.route("/refresh", methods=["POST"])
def refresh():
    """
    POST /api/v1/auth/refresh
    Refresh access token menggunakan refresh token

    Request Body:
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

    Returns:
        200: Access token baru
        401: Refresh token tidak valid atau expired
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body is required"}), 400

        try:
            refresh_request = RefreshTokenRequest(**data)
        except ValidationError:
            return jsonify({"status": "error", "message": "Validation failed"}), 400

        # Verifikasi refresh token
        payload = verify_token(refresh_request.refresh_token, token_type="refresh")

        if not payload:
            return jsonify({"status": "error", "message": "Invalid or expired refresh token"}), 401

        # Ambil data user
        user_id = payload.get("sub")

        with get_db() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user or not user.is_active:
                return jsonify({"status": "error", "message": "User not found or inactive"}), 401

            # Buat access token baru
            user_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "permissions": user.get_permissions(),
                "factory_id": user.factory_id,
                "department": user.department,
            }

            access_token = create_access_token(user_data)

            return (
                jsonify(
                    {
                        "status": "success",
                        "access_token": access_token,
                        "token_type": "Bearer",
                        "expires_in": config.JWT_ACCESS_TOKEN_EXPIRES,
                    }
                ),
                200,
            )

    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@bp.route("/me", methods=["GET"])
@require_auth
def get_current_user():
    """
    GET /api/v1/auth/me
    Mengambil informasi user yang sedang login

    Returns:
        200: Informasi user
        401: Tidak terautentikasi
    """
    user = g.current_user
    return jsonify({"status": "success", "user": user.to_dict(include_permissions=True)}), 200


@bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """
    POST /api/v1/auth/logout
    Logout user (client harus menghapus token)

    Returns:
        200: Logout berhasil
    """
    user = g.current_user

    # Log audit logout
    log_audit(user=user, action="LOGOUT", resource="/api/v1/auth/logout", method="POST", status_code=200)

    # Blacklist token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        blacklist_token(token, ttl=config.JWT_ACCESS_TOKEN_EXPIRES)

    logger.info(f"User logged out: {user.username}")

    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
