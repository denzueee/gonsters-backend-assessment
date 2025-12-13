from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging

from app.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

engine = None
SessionLocal = None


def init_postgres_db():
    """
    Inisialisasi koneksi PostgreSQL dengan connection pooling
    
    Returns:
        Engine: Instance SQLAlchemy Engine
    """
    global engine, SessionLocal
    
    config = get_config()
    
    try:
        # Bikin engine dengan pooling
        engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            poolclass=QueuePool,
            **config.SQLALCHEMY_ENGINE_OPTIONS,
            echo=config.DEBUG
        )
        
        # Register event listeners setelah engine dibuat
        @event.listens_for(engine, "connect", insert=True)
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("New database connection created")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            logger.debug("Connection returned to pool")
        
        # Setup session factory
        session_factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False
        )
        
        # Pake scoped_session biar thread-safe
        SessionLocal = scoped_session(session_factory)
        
        # Test koneksi
        with engine.connect() as conn:
            logger.info("PostgreSQL connection established successfully")
            
        return engine
        
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise


def get_db_session():
    """Mengambil session database baru"""
    if SessionLocal is None:
        init_postgres_db()
    return SessionLocal()


@contextmanager
def get_db():
    """
    Context manager untuk session database
    Otomatis cleanup dan handle error
    
    Yields:
        Session: Database session
    """
    db = get_db_session()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


def close_db_connection():
    """Menutup koneksi database dan membersihkan resources"""
    global engine, SessionLocal
    
    if SessionLocal:
        SessionLocal.remove()
        logger.info("Database sessions closed")
    
    if engine:
        engine.dispose()
        logger.info("Database engine disposed")

