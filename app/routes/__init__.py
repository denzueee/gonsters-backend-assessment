"""
Routes package initialization
"""

from app.routes.data_routes import bp as data_bp
from app.routes.auth_routes import bp as auth_bp
from app.routes.config_routes import bp as config_bp

__all__ = ["data_bp", "auth_bp", "config_bp"]
