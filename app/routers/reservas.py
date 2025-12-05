"""
Router para gestión de reservas - MVP Simplificado
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date
from app.database import get_db
from app import models, schemas

router = APIRouter()


def verificar_disponibilidad(
    db: Session,
    nombre_habitacion: str,
    fecha_entrada: date,
    fecha_salida: date,
    reserva_id_excluir: Optional[int] = None
) -> bool:
    """
    Verifica si una habitación está disponible en un rango de fechas
    """
    # Buscar reservas que se solapen con el rango de fechas
    query = db.query(models.Reserva).filter(
        models.Reserva.nombre_habitacion == nombre_habitacion,
        models.Reserva.estado.in_(["pendiente", "confirmada"]),
        or_(
            and_(
                models.Reserva.fecha_entrada <= fecha_entrada,
                models.Reserva.fecha_salida > fecha_entrada
            ),
            and_(
                models.Reserva.fecha_entrada < fecha_salida,
                models.Reserva.fecha_salida >= fecha_salida
            ),
            and_(
                models.Reserva.fecha_entrada >= fecha_entrada,
                models.Reserva.fecha_salida <= fecha_salida
            )
        )
    )
    
    if reserva_id_excluir:
        query = query.filter(models.Reserva.id != reserva_id_excluir)
    
    reserva_conflicto = query.first()
    return reserva_conflicto is None


@router.post(
    "/reservas",
    response_model=schemas.ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva reserva",
    description="Crea una nueva reserva verificando disponibilidad básica"
)
async def crear_reserva(
    reserva: schemas.ReservaCreate,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva reserva
    
    - **nombre_cliente**: Nombre completo del cliente
    - **nombre_habitacion**: Nombre de la habitación
    - **fecha_entrada**: Fecha de entrada
    - **fecha_salida**: Fecha de salida (debe ser posterior a fecha_entrada)
    - **numero_huespedes**: Número de huéspedes
    - **precio_total**: Precio total de la reserva
    - **telefono**: Teléfono de contacto (opcional)
    - **email**: Email del cliente (opcional)
    - **notas**: Notas adicionales (opcional)
    """
    # Validar fechas
    if reserva.fecha_entrada >= reserva.fecha_salida:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de salida debe ser posterior a la fecha de entrada"
        )
    
    if reserva.fecha_entrada < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de entrada no puede ser en el pasado"
        )
    
    # Verificar disponibilidad básica
    if not verificar_disponibilidad(db, reserva.nombre_habitacion, reserva.fecha_entrada, reserva.fecha_salida):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La habitación '{reserva.nombre_habitacion}' no está disponible en el rango de fechas seleccionado"
        )
    
    # Crear reserva
    db_reserva = models.Reserva(
        nombre_cliente=reserva.nombre_cliente,
        nombre_habitacion=reserva.nombre_habitacion,
        fecha_entrada=reserva.fecha_entrada,
        fecha_salida=reserva.fecha_salida,
        numero_huespedes=reserva.numero_huespedes,
        precio_total=reserva.precio_total,
        estado=reserva.estado or "pendiente",
        telefono=reserva.telefono,
        email=reserva.email,
        notas=reserva.notas
    )
    
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    
    return db_reserva


@router.get(
    "/reservas",
    response_model=List[schemas.ReservaResponse],
    summary="Listar todas las reservas",
    description="Obtiene una lista de todas las reservas con opciones de filtrado básico"
)
async def listar_reservas(
    skip: int = 0,
    limit: int = 100,
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    nombre_cliente: Optional[str] = Query(None, description="Filtrar por nombre de cliente"),
    nombre_habitacion: Optional[str] = Query(None, description="Filtrar por nombre de habitación"),
    fecha_desde: Optional[date] = Query(None, description="Filtrar desde fecha"),
    fecha_hasta: Optional[date] = Query(None, description="Filtrar hasta fecha"),
    db: Session = Depends(get_db)
):
    """
    Listar reservas
    
    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de registros a retornar
    - **estado**: Filtrar por estado (pendiente, confirmada, cancelada, completada)
    - **nombre_cliente**: Filtrar por nombre de cliente (búsqueda parcial)
    - **nombre_habitacion**: Filtrar por nombre de habitación
    - **fecha_desde**: Filtrar reservas desde esta fecha
    - **fecha_hasta**: Filtrar reservas hasta esta fecha
    """
    query = db.query(models.Reserva)
    
    if estado:
        query = query.filter(models.Reserva.estado == estado)
    
    if nombre_cliente:
        query = query.filter(models.Reserva.nombre_cliente.contains(nombre_cliente))
    
    if nombre_habitacion:
        query = query.filter(models.Reserva.nombre_habitacion == nombre_habitacion)
    
    if fecha_desde:
        query = query.filter(models.Reserva.fecha_entrada >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(models.Reserva.fecha_salida <= fecha_hasta)
    
    reservas = query.order_by(models.Reserva.fecha_entrada.desc()).offset(skip).limit(limit).all()
    return reservas


@router.get(
    "/reservas/{reserva_id}",
    response_model=schemas.ReservaResponse,
    summary="Obtener reserva por ID",
    description="Obtiene los detalles completos de una reserva específica"
)
async def obtener_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener reserva por ID
    
    - **reserva_id**: ID de la reserva a consultar
    """
    reserva = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    return reserva


@router.put(
    "/reservas/{reserva_id}",
    response_model=schemas.ReservaResponse,
    summary="Actualizar reserva",
    description="Actualiza una reserva existente, verificando disponibilidad si se cambian las fechas o habitación"
)
async def actualizar_reserva(
    reserva_id: int,
    reserva_update: schemas.ReservaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar reserva
    
    - **reserva_id**: ID de la reserva a actualizar
    - Si se cambian las fechas o habitación, se verifica disponibilidad
    """
    db_reserva = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()
    
    if not db_reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    # Si la reserva está cancelada o completada, no se puede modificar
    if db_reserva.estado in ["cancelada", "completada"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede modificar una reserva con estado '{db_reserva.estado}'"
        )
    
    fecha_entrada = reserva_update.fecha_entrada or db_reserva.fecha_entrada
    fecha_salida = reserva_update.fecha_salida or db_reserva.fecha_salida
    nombre_habitacion = reserva_update.nombre_habitacion or db_reserva.nombre_habitacion
    
    # Si se cambian las fechas o habitación, validar disponibilidad
    if (reserva_update.fecha_entrada or reserva_update.fecha_salida or 
        reserva_update.nombre_habitacion):
        if fecha_entrada >= fecha_salida:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de salida debe ser posterior a la fecha de entrada"
            )
        
        # Verificar disponibilidad (excluyendo la reserva actual)
        if not verificar_disponibilidad(db, nombre_habitacion, fecha_entrada, fecha_salida, reserva_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La habitación '{nombre_habitacion}' no está disponible en el nuevo rango de fechas"
            )
    
    # Actualizar campos
    update_data = reserva_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reserva, field, value)
    
    db.commit()
    db.refresh(db_reserva)
    
    return db_reserva


@router.patch(
    "/reservas/{reserva_id}/confirmar",
    response_model=schemas.ReservaResponse,
    summary="Confirmar reserva",
    description="Confirma una reserva pendiente"
)
async def confirmar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Confirmar reserva
    
    - **reserva_id**: ID de la reserva a confirmar
    - Cambia el estado de "pendiente" a "confirmada"
    """
    reserva = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    if reserva.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden confirmar reservas pendientes. Estado actual: {reserva.estado}"
        )
    
    reserva.estado = "confirmada"
    db.commit()
    db.refresh(reserva)
    
    return reserva


@router.patch(
    "/reservas/{reserva_id}/cancelar",
    response_model=schemas.ReservaResponse,
    summary="Cancelar reserva",
    description="Cancela una reserva pendiente o confirmada"
)
async def cancelar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancelar reserva
    
    - **reserva_id**: ID de la reserva a cancelar
    - Cambia el estado a "cancelada"
    """
    reserva = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    if reserva.estado == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La reserva ya está cancelada"
        )
    
    if reserva.estado == "completada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una reserva completada"
        )
    
    reserva.estado = "cancelada"
    db.commit()
    db.refresh(reserva)
    
    return reserva


@router.delete(
    "/reservas/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar reserva",
    description="Elimina una reserva del sistema (solo si está cancelada)"
)
async def eliminar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar reserva
    
    - **reserva_id**: ID de la reserva a eliminar
    - Solo se pueden eliminar reservas canceladas
    """
    reserva = db.query(models.Reserva).filter(
        models.Reserva.id == reserva_id
    ).first()
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva con ID {reserva_id} no encontrada"
        )
    
    if reserva.estado != "cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden eliminar reservas canceladas. Estado actual: {reserva.estado}"
        )
    
    db.delete(reserva)
    db.commit()
    
    return None
