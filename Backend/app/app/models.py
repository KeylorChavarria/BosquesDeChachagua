"""
Modelos de base de datos (SQLAlchemy) - MVP Simplificado
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from app.database import Base


class Reserva(Base):
    """
    Modelo de Reserva - MVP Simplificado
    """
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    nombre_cliente = Column(String(100), nullable=False, index=True)
    nombre_habitacion = Column(String(50), nullable=False, index=True)
    fecha_entrada = Column(Date, nullable=False, index=True)
    fecha_salida = Column(Date, nullable=False, index=True)
    numero_huespedes = Column(Integer, nullable=False)
    precio_total = Column(Float, nullable=False)
    estado = Column(String(20), default="pendiente")  # pendiente, confirmada, cancelada, completada
    telefono = Column(String(20))  # Opcional pero útil
    email = Column(String(100))  # Opcional pero útil
    notas = Column(String(500))  # Opcional
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
