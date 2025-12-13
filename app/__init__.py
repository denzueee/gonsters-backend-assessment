"""
Flask Application Factory
Initializes Flask app with database connections and routes
"""

from flask import Flask
from flask_cors import CORS
import logging

from app.config import get_config
from app.database import init_postgres_db, init_influxdb

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Membuat dan konfigurasi aplikasi Flask

    Args:
        config_name: Nama environment (development, production, testing)

    Returns:
        Flask: Instance aplikasi Flask yang sudah dikonfigurasi
    """
    app = Flask(__name__)

    # Load configuration
    if config_name:
        app.config.from_object(f"app.config.{config_name.capitalize()}Config")
    else:
        config = get_config()
        app.config.from_object(config)

    # Enable CORS
    CORS(app)

    # Initialize databases
    with app.app_context():
        try:
            # Initialize PostgreSQL
            init_postgres_db()
            logger.info("PostgreSQL initialized")

            # Initialize InfluxDB
            init_influxdb()
            logger.info("InfluxDB initialized")

        except Exception as e:
            logger.error(f"Failed to initialize databases: {str(e)}")
            raise

    # Register blueprints
    from app.routes import data_bp, auth_bp, config_bp

    app.register_blueprint(data_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(config_bp)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "GONSTERS Backend Assessment", "version": "1.0.0"}, 200

    @app.route("/", methods=["GET"])
    def index():
        """Root endpoint"""
        return {
            "message": "GONSTERS Backend Assessment API",
            "version": "1.0.0",
            "endpoints": {"health": "/health", "docs": "/docs"},
        }, 200

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
