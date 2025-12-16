"""
Model System Configuration
SQLAlchemy ORM model untuk tabel system_config
"""

import uuid

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database.postgres import Base


class SystemConfig(Base):
    """
    Model System Configuration

    Menyimpan konfigurasi sistem secara persistent di database.
    Menggunakan key-value pattern untuk fleksibilitas.

    Attributes:
        id: Identifier unik config (UUID)
        setting_name: Nama setting (unique key)
        setting_value: Nilai setting (sebagai string)
        description: Deskripsi setting (opsional)
        updated_by: Username yang terakhir update
        created_at: Timestamp pembuatan record
        updated_at: Timestamp update terakhir
    """

    __tablename__ = "system_config"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Config Key-Value
    setting_name = Column(String(255), nullable=False, unique=True, index=True)
    setting_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)

    # Audit
    updated_by = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<SystemConfig(setting_name='{self.setting_name}', value='{self.setting_value}')>"

    def to_dict(self):
        """
        Konversi instance model ke dictionary

        Returns:
            dict: Config sebagai dictionary
        """
        return {
            "id": str(self.id),
            "setting_name": self.setting_name,
            "setting_value": self.setting_value,
            "description": self.description,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """
        Buat instance model dari dictionary

        Args:
            data: Dictionary berisi config data

        Returns:
            SystemConfig: Instance baru
        """
        return cls(
            setting_name=data.get("setting_name"),
            setting_value=data.get("setting_value"),
            description=data.get("description"),
            updated_by=data.get("updated_by"),
        )
