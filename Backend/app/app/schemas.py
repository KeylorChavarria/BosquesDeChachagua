"""
Esquemas Pydantic para validación y serialización - MVP Simplificado
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date, datetime
from typing import Optional, List


# ==================== SCHEMAS DE RESERVA ====================

class ReservaBase(BaseModel):
    nombre_cliente: str = Field(..., min_length=1, description="Nombre del cliente", example="Juan Pérez")
    nombre_habitacion: str = Field(..., min_length=1, description="Nombre de la habitación", example="Habitación 101")
    fecha_entrada: date = Field(..., description="Fecha de entrada", example="2024-12-01")
    fecha_salida: date = Field(..., description="Fecha de salida", example="2024-12-05")
    numero_huespedes: int = Field(..., gt=0, description="Número de huéspedes", example=2)
    precio_total: float = Field(..., gt=0, description="Precio total de la reserva", example=600.00)
    telefono: Optional[str] = Field(None, description="Teléfono de contacto", example="+506 8888-8888")
    email: Optional[EmailStr] = Field(None, description="Email del cliente", example="juan@email.com")
    notas: Optional[str] = Field(None, description="Notas adicionales sobre la reserva")


class ReservaCreate(ReservaBase):
    estado: Optional[str] = Field("pendiente", description="Estado inicial de la reserva")


class ReservaUpdate(BaseModel):
    nombre_cliente: Optional[str] = Field(None, min_length=1)
    nombre_habitacion: Optional[str] = Field(None, min_length=1)
    fecha_entrada: Optional[date] = None
    fecha_salida: Optional[date] = None
    numero_huespedes: Optional[int] = Field(None, gt=0)
    precio_total: Optional[float] = Field(None, gt=0)
    estado: Optional[str] = Field(None, description="Estado: pendiente, confirmada, cancelada, completada")
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    notas: Optional[str] = None


class ReservaResponse(ReservaBase):
    id: int
    estado: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
