"""
Configuration routes (protected endpoints)
Demonstrates RBAC with Management-only access
Uses PostgreSQL database for persistent configuration storage
"""

import logging

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError

from app.auth import log_audit, log_successful_request, require_auth, require_permission
from app.database import get_db
from app.models import SystemConfig
from app.schemas import ConfigUpdateRequest
from app.utils import cache_response, invalidate_cache

bp = Blueprint("config", __name__, url_prefix="/api/v1/config")
logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG = {
    "max_temperature_threshold": "80.0",
    "min_temperature_threshold": "50.0",
    "max_pressure_threshold": "150.0",
    "alert_email": "alerts@factory.com",
    "data_retention_days": "365",
}


def initialize_default_config():
    """
    Initialize default configuration values in database if not exists.
    Called on application startup.
    """
    try:
        with get_db() as db:
            for setting_name, setting_value in DEFAULT_CONFIG.items():
                existing = db.query(SystemConfig).filter(SystemConfig.setting_name == setting_name).first()
                if not existing:
                    config = SystemConfig(
                        setting_name=setting_name,
                        setting_value=setting_value,
                        description=f"Default value for {setting_name}",
                        updated_by="system",
                    )
                    db.add(config)
            db.commit()
            logger.info("Default configuration initialized in database")
    except Exception as e:
        logger.error(f"Failed to initialize default config: {e}")


def get_config_value(setting_name, default=None):
    """
    Get a single configuration value from database with caching

    Args:
        setting_name: Name of the setting
        default: Default value if not found

    Returns:
        str: Configuration value
    """
    try:
        with get_db() as db:
            config = db.query(SystemConfig).filter(SystemConfig.setting_name == setting_name).first()
            if config:
                return config.setting_value
            return default
    except Exception as e:
        logger.error(f"Failed to get config value {setting_name}: {e}")
        return default


def get_all_config():
    """
    Get all configuration values from database as dictionary

    Returns:
        dict: All configuration key-value pairs
    """
    try:
        with get_db() as db:
            configs = db.query(SystemConfig).all()
            return {config.setting_name: config.setting_value for config in configs}
    except Exception as e:
        logger.error(f"Failed to get all config: {e}")
        return DEFAULT_CONFIG.copy()


@bp.route("", methods=["GET"])
@require_auth
@require_permission("read:config")
@cache_response(timeout=300, key_prefix="config")
def get_config():
    """
    GET /api/v1/config
    Mengambil konfigurasi sistem dari database

    Required Permission: read:config
    Allowed Roles: Management

    Returns:
        200: Data konfigurasi
        403: Permission tidak mencukupi
    """

    user = g.current_user

    # Get all config from database
    config_dict = get_all_config()

    log_successful_request()

    return (
        jsonify({"status": "success", "config": config_dict, "accessed_by": user.username, "source": "database"}),
        200,
    )


@bp.route("/update", methods=["POST"])
@require_auth
@require_permission("write:config")
def update_config():
    """
    POST /api/v1/config/update
    Update konfigurasi sistem di database

    Required Permission: write:config
    Allowed Roles: Management only

    Request Body:
        {
            "setting_name": "max_temperature_threshold",
            "setting_value": "85.0"
        }

    Returns:
        200: Konfigurasi diperbarui
        400: Error validasi
        403: Permission tidak mencukupi
    """

    try:
        user = g.current_user

        # Validasi request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body is required"}), 400

        try:
            config_request = ConfigUpdateRequest(**data)
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

        with get_db() as db:
            # Find existing config
            config = db.query(SystemConfig).filter(SystemConfig.setting_name == config_request.setting_name).first()

            old_value = None

            if config:
                # Update existing
                old_value = config.setting_value
                config.setting_value = config_request.setting_value
                config.updated_by = user.username
            else:
                # Create new
                config = SystemConfig(
                    setting_name=config_request.setting_name,
                    setting_value=config_request.setting_value,
                    updated_by=user.username,
                    description=f"Custom setting for {config_request.setting_name}",
                )
                db.add(config)

            db.commit()

            # Log audit
            log_audit(
                user=user, action="UPDATE_CONFIG", resource="/api/v1/config/update", method="POST", status_code=200
            )

            logger.info(
                f"Config updated by {user.username}: "
                f"{config_request.setting_name} = {config_request.setting_value} "
                f"(was: {old_value})"
            )

            # Invalidate cache
            invalidate_cache("cache:config:*")

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Configuration updated successfully",
                        "updated_setting": {
                            "name": config_request.setting_name,
                            "old_value": old_value,
                            "new_value": config_request.setting_value,
                            "updated_by": user.username,
                            "updated_at": (
                                config.updated_at.isoformat()
                                if hasattr(config.updated_at, "isoformat")
                                else str(config.updated_at)
                            ),
                        },
                    }
                ),
                200,
            )

    except Exception as e:
        logger.error(f"Config update error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@bp.route("/reset", methods=["POST"])
@require_auth
@require_permission("write:config")
def reset_config():
    """
    POST /api/v1/config/reset
    Reset konfigurasi ke default di database

    Required Permission: write:config
    Allowed Roles: Management only

    Returns:
        200: Konfigurasi di-reset
        403: Permission tidak mencukupi
    """

    user = g.current_user

    try:
        with get_db() as db:
            # Delete all existing config
            db.query(SystemConfig).delete()

            # Re-initialize with defaults
            for setting_name, setting_value in DEFAULT_CONFIG.items():
                config = SystemConfig(
                    setting_name=setting_name,
                    setting_value=setting_value,
                    description=f"Default value for {setting_name}",
                    updated_by=user.username,
                )
                db.add(config)

            db.commit()

        log_audit(user=user, action="RESET_CONFIG", resource="/api/v1/config/reset", method="POST", status_code=200)

        logger.warning(f"Config reset to defaults by {user.username}")

        # Invalidate cache
        invalidate_cache("cache:config:*")

        return (
            jsonify({"status": "success", "message": "Configuration reset to defaults", "config": DEFAULT_CONFIG}),
            200,
        )

    except Exception as e:
        logger.error(f"Config reset error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
