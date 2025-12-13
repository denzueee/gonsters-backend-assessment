"""
Configuration routes (protected endpoints)
Demonstrates RBAC with Management-only access
"""

from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
import logging

from app.auth import require_auth, require_permission, log_audit, log_successful_request
from app.schemas import ConfigUpdateRequest
from app.utils import cache_response, invalidate_cache

bp = Blueprint('config', __name__, url_prefix='/api/v1/config')
logger = logging.getLogger(__name__)

# Mock penyimpanan konfigurasi (seharusnya database)
CONFIG_STORE = {
    'max_temperature_threshold': '80.0',
    'max_pressure_threshold': '150.0',
    'alert_email': 'alerts@factory.com',
    'data_retention_days': '365'
}


@bp.route('', methods=['GET'])
@require_auth
@require_permission('read:config')
@cache_response(timeout=300, key_prefix='config')
def get_config():
    """
    GET /api/v1/config
    Mengambil konfigurasi sistem
    
    Required Permission: read:config
    Allowed Roles: Management
    
    Returns:
        200: Data konfigurasi
        403: Permission tidak mencukupi
    """

    user = g.current_user
    
    log_successful_request()
    
    return jsonify({
        'status': 'success',
        'config': CONFIG_STORE,
        'accessed_by': user.username
    }), 200


@bp.route('/update', methods=['POST'])
@require_auth
@require_permission('write:config')
def update_config():
    """
    POST /api/v1/config/update
    Update konfigurasi sistem
    
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
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        try:
            config_request = ConfigUpdateRequest(**data)
        except ValidationError as e:
            return jsonify({
                'status': 'error',
                'message': 'Validation failed',
                'errors': [{'field': '.'.join(str(loc) for loc in err['loc']), 'error': err['msg']} for err in e.errors()]
            }), 400
        
        # Simpan nilai lama
        old_value = CONFIG_STORE.get(config_request.setting_name)

        # Update konfigurasi
        CONFIG_STORE[config_request.setting_name] = config_request.setting_value
        
        # Log audit
        log_audit(
            user=user,
            action='UPDATE_CONFIG',
            resource=f'/api/v1/config/update',
            method='POST',
            status_code=200
        )
        
        logger.info(
            f"Config secured updated by {user.username}: "
            f"{config_request.setting_name} = {config_request.setting_value} "
            f"(was: {old_value})"
        )
        
        # Invalidate cache
        invalidate_cache("cache:config:*")
        
        return jsonify({
            'status': 'success',
            'message': 'Configuration updated successfully',
            'updated_setting': {
                'name': config_request.setting_name,
                'old_value': old_value,
                'new_value': config_request.setting_value,
                'updated_by': user.username,
                'updated_at': 'datetime.utcnow().isoformat()'
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Config update error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500


@bp.route('/reset', methods=['POST'])
@require_auth
@require_permission('write:config')
def reset_config():
    """
    POST /api/v1/config/reset
    Reset konfigurasi ke default
    
    Required Permission: write:config
    Allowed Roles: Management only
    
    Returns:
        200: Konfigurasi di-reset
        403: Permission tidak mencukupi
    """

    user = g.current_user
    
    # Reset ke default
    global CONFIG_STORE
    CONFIG_STORE = {
        'max_temperature_threshold': '80.0',
        'max_pressure_threshold': '150.0',
        'alert_email': 'alerts@factory.com',
        'data_retention_days': '365'
    }
    
    log_audit(
        user=user,
        action='RESET_CONFIG',
        resource='/api/v1/config/reset',
        method='POST',
        status_code=200
    )
    
    logger.warning(f"Config reset to defaults by {user.username}")
    
    # Invalidate cache
    invalidate_cache("cache:config:*")
    
    return jsonify({
        'status': 'success',
        'message': 'Configuration reset to defaults',
        'config': CONFIG_STORE
    }), 200
