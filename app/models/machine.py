"""
Model Metadata Mesin
SQLAlchemy ORM model untuk tabel machine_metadata
"""

from sqlalchemy import Column, String, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.database.postgres import Base


class MachineMetadata(Base):
    """
    Model Metadata Mesin
    
    Merepresentasikan mesin industri dengan metadata seperti
    lokasi, tipe sensor, dan status operasional.
    
    Attributes:
        id: Identifier unik mesin (UUID)
        name: Nama mesin
        location: Lokasi fisik
        sensor_type: Tipe sensor yang terpasang
        status: Status operasional saat ini
        created_at: Timestamp pembuatan record
        updated_at: Timestamp update terakhir record
    """
    
    __tablename__ = 'machine_metadata'
    
    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    
    # Informasi Mesin
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(500), nullable=False, index=True)
    sensor_type = Column(String(100), nullable=False, index=True)
    
    # Status dengan constraint
    status = Column(
        String(50),
        nullable=False,
        default='active',
        index=True
    )
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Constraints tabel
    __table_args__ = (
        CheckConstraint(
            status.in_(['active', 'inactive', 'maintenance', 'error']),
            name='chk_status'
        ),
    )
    
    def __repr__(self):
        return f"<MachineMetadata(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self):
        """
        Konversi instance model ke dictionary
        
        Returns:
            dict: Metadata mesin sebagai dictionary
        """
        return {
            'id': str(self.id),
            'name': self.name,
            'location': self.location,
            'sensor_type': self.sensor_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Buat instance model dari dictionary
        
        Args:
            data: Dictionary berisi metadata mesin
        
        Returns:
            MachineMetadata: Instance baru
        """
        return cls(
            name=data.get('name'),
            location=data.get('location'),
            sensor_type=data.get('sensor_type'),
            status=data.get('status', 'active')
        )
