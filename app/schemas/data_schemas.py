"""
Pydantic schemas untuk validasi request/response
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class SensorReading(BaseModel):
    timestamp: datetime = Field(..., description="Waktu pengukuran dalam format ISO 8601")
    temperature: Optional[float] = Field(None, description="Temperatur dalam Celsius", ge=-273.15, le=1000)
    pressure: Optional[float] = Field(None, description="Tekanan dalam kPa", ge=0, le=10000)
    speed: Optional[float] = Field(None, description="Kecepatan dalam RPM", ge=0, le=100000)

    @validator("temperature", "pressure", "speed")
    def at_least_one_field(cls, v, values):
        """Pastikan setidaknya satu nilai sensor ada"""
        if v is None and all(values.get(field) is None for field in ["temperature", "pressure", "speed"]):
            raise ValueError("Minimal satu nilai sensor (temperature, pressure, atau speed) harus diisi")
        return v

    class Config:
        json_schema_extra = {
            "example": {"timestamp": "2025-12-13T03:38:50Z", "temperature": 72.5, "pressure": 101.3, "speed": 1450.0}
        }


class MachineData(BaseModel):
    machine_id: UUID = Field(..., description="UUID Mesin dari PostgreSQL")
    sensor_type: str = Field(..., description="Tipe sensor", min_length=1, max_length=100)
    location: str = Field(..., description="Lokasi fisik", min_length=1, max_length=500)
    readings: List[SensorReading] = Field(..., description="Array pembacaan sensor", min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "machine_id": "d1c2084b-f16a-4eea-89d9-4402095d3af5",
                "sensor_type": "Temperature",
                "location": "Factory Floor 1 - Zone A",
                "readings": [{"timestamp": "2025-12-13T03:38:50Z", "temperature": 72.5, "pressure": 101.3}],
            }
        }


class IngestRequest(BaseModel):
    gateway_id: str = Field(..., description="Identifier Gateway", min_length=1, max_length=255)
    timestamp: datetime = Field(..., description="Waktu transmisi Gateway")
    batch: List[MachineData] = Field(..., description="Batch data mesin", min_items=1, max_items=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "gateway_id": "gateway-001",
                "timestamp": "2025-12-13T03:38:52Z",
                "batch": [
                    {
                        "machine_id": "d1c2084b-f16a-4eea-89d9-4402095d3af5",
                        "sensor_type": "Temperature",
                        "location": "Factory Floor 1 - Zone A",
                        "readings": [{"timestamp": "2025-12-13T03:38:50Z", "temperature": 72.5, "pressure": 101.3}],
                    }
                ],
            }
        }


class MachineDetail(BaseModel):
    machine_id: str
    readings_count: int
    status: str


class IngestResponse(BaseModel):
    status: str
    message: str
    summary: dict
    details: List[MachineDetail]


class ErrorDetail(BaseModel):
    field: str
    error: str
    value: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str
    message: str
    errors: Optional[List[ErrorDetail]] = None


class DataPoint(BaseModel):
    timestamp: datetime
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    speed: Optional[float] = None


class MachineInfo(BaseModel):
    machine_id: str
    name: str
    location: str
    sensor_type: str


class QueryInfo(BaseModel):
    start_time: datetime
    end_time: datetime
    interval: str
    fields: List[str]


class PaginationInfo(BaseModel):
    total_records: int
    returned_records: int
    limit: int
    offset: int
    has_more: bool


class RetrievalResponse(BaseModel):
    status: str
    machine: MachineInfo
    query: QueryInfo
    data: List[DataPoint]
    pagination: PaginationInfo


class CreateMachineRequest(BaseModel):
    name: str = Field(..., description="Nama mesin", min_length=1, max_length=255)
    location: str = Field(..., description="Lokasi mesin", min_length=1, max_length=500)
    sensor_type: str = Field(..., description="Tipe sensor utama", min_length=1, max_length=100)
    status: Optional[str] = Field("active", description="Status awal ('active', 'inactive', 'maintenance', 'error')")

    @validator("status")
    def validate_status(cls, v):
        allowed = ["active", "inactive", "maintenance", "error"]
        if v not in allowed:
            raise ValueError(f'Status harus salah satu dari: {", ".join(allowed)}')
        return v


class MachineListResponse(BaseModel):
    status: str
    count: int
    machines: List[MachineInfo]
