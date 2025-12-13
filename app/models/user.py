"""
Model User untuk autentikasi dan RBAC
"""

from sqlalchemy import Column, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import bcrypt

from app.database import Base


class User(Base):
    
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='Operator', index=True)
    factory_id = Column(String(50), index=True)
    department = Column(String(100))
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint(role.in_(['Operator', 'Supervisor', 'Management']), name='chk_role'),
    )
    
    # Mapping Role-Permission
    ROLE_PERMISSIONS = {
        'Operator': [
            'read:machines',
            'read:sensor_data',
            'write:sensor_data'
        ],
        'Supervisor': [
            'read:machines',
            'write:machines',
            'read:sensor_data',
            'write:sensor_data',
            'read:reports',
            'write:reports'
        ],
        'Management': [
            'read:machines',
            'write:machines',
            'delete:machines',
            'read:sensor_data',
            'write:sensor_data',
            'delete:sensor_data',
            'read:config',
            'write:config',
            'read:users',
            'write:users',
            'delete:users',
            'read:reports',
            'write:reports'
        ]
    }
    
    def set_password(self, password: str):
        """Hash dan set password"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifikasi password terhadap hash"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def get_permissions(self) -> list:
        """Mengambil permissions sesuai role user"""
        return self.ROLE_PERMISSIONS.get(self.role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Cek apakah user memiliki permission tertentu"""
        return permission in self.get_permissions()
    
    def to_dict(self, include_permissions=False):
        """Konversi object user ke dictionary"""
        data = {
            'id': str(self.id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'factory_id': self.factory_id,
            'department': self.department,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_permissions:
            data['permissions'] = self.get_permissions()
        
        return data
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class AuditLog(Base):
    
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), index=True)
    username = Column(String(50))
    role = Column(String(20))
    action = Column(String(100), nullable=False, index=True)
    resource = Column(String(255), nullable=False, index=True)
    method = Column(String(10))
    status_code = Column(String(10))
    ip_address = Column(String(45))
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def to_dict(self):
        """Konversi audit log ke dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id) if self.user_id else None,
            'username': self.username,
            'role': self.role,
            'action': self.action,
            'resource': self.resource,
            'method': self.method,
            'status_code': self.status_code,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<AuditLog {self.username} {self.action} {self.resource}>"
