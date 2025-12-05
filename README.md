# Bosques de Chachagua - Sistema de Reservas (MVP)

Sistema de gestión de reservas para el hotel Bosques de Chachagua, desarrollado con FastAPI. Versión MVP simplificada.

## 🚀 Características

- **Gestión de Reservas**: CRUD completo para reservas
- **Verificación de Disponibilidad**: Verifica automáticamente disponibilidad al crear reservas
- **Documentación Automática**: Swagger UI y ReDoc integrados
- **Validación de Datos**: Validación automática con Pydantic
- **Base de Datos**: SQLAlchemy con SQLite

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Navegar al directorio del proyecto:
```bash
cd /var/www/html/BosquesDeChachagua
```

2. Crear un entorno virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🏃 Ejecución

Para iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O usando Python directamente:

```bash
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

## 📚 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🛣️ Endpoints

### Reservas (`/api/v1/reservas`)

- `POST /api/v1/reservas` - Crear nueva reserva
- `GET /api/v1/reservas` - Listar todas las reservas (con filtros opcionales)
- `GET /api/v1/reservas/{reserva_id}` - Obtener reserva por ID
- `PUT /api/v1/reservas/{reserva_id}` - Actualizar reserva
- `PATCH /api/v1/reservas/{reserva_id}/confirmar` - Confirmar reserva
- `PATCH /api/v1/reservas/{reserva_id}/cancelar` - Cancelar reserva
- `DELETE /api/v1/reservas/{reserva_id}` - Eliminar reserva (solo canceladas)

### Sistema

- `GET /` - Endpoint raíz con información de la API
- `GET /health` - Health check del sistema

## 📊 Modelo de Datos

### Reserva (MVP Simplificado)
- `id`: Identificador único
- `nombre_cliente`: Nombre completo del cliente
- `nombre_habitacion`: Nombre de la habitación
- `fecha_entrada`: Fecha de entrada
- `fecha_salida`: Fecha de salida
- `numero_huespedes`: Número de huéspedes
- `precio_total`: Precio total de la reserva
- `estado`: Estado de la reserva (pendiente, confirmada, cancelada, completada)
- `telefono`: Teléfono de contacto (opcional)
- `email`: Email del cliente (opcional)
- `notas`: Notas adicionales (opcional)

## 🔒 Validaciones Implementadas

- **Reservas**: 
  - Verificación de disponibilidad de habitaciones por nombre
  - Validación de fechas (entrada < salida, no fechas pasadas)
  - Prevención de solapamiento de reservas para la misma habitación

## 🗄️ Base de Datos

El sistema utiliza SQLite por defecto (`bosques_chachagua.db`). Para cambiar a PostgreSQL o MySQL, modifica la URL de conexión en `app/database.py`:

```python
# PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://usuario:password@localhost/bosques_chachagua"

# MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://usuario:password@localhost/bosques_chachagua"
```

## 🧪 Ejemplos de Uso

### Crear una reserva
```bash
curl -X POST "http://localhost:8000/api/v1/reservas" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_cliente": "Juan Pérez",
    "nombre_habitacion": "Habitación 101",
    "fecha_entrada": "2024-12-01",
    "fecha_salida": "2024-12-05",
    "numero_huespedes": 2,
    "precio_total": 600.00,
    "telefono": "+506 8888-8888",
    "email": "juan@email.com"
  }'
```

### Listar todas las reservas
```bash
curl "http://localhost:8000/api/v1/reservas"
```

### Listar reservas filtradas
```bash
curl "http://localhost:8000/api/v1/reservas?estado=confirmada&nombre_habitacion=Habitación%20101"
```

### Obtener una reserva específica
```bash
curl "http://localhost:8000/api/v1/reservas/1"
```

### Actualizar una reserva
```bash
curl -X PUT "http://localhost:8000/api/v1/reservas/1" \
  -H "Content-Type: application/json" \
  -d '{
    "precio_total": 700.00,
    "notas": "Cliente VIP"
  }'
```

### Confirmar una reserva
```bash
curl -X PATCH "http://localhost:8000/api/v1/reservas/1/confirmar"
```

### Cancelar una reserva
```bash
curl -X PATCH "http://localhost:8000/api/v1/reservas/1/cancelar"
```

## 📝 Notas

- La documentación Swagger se genera automáticamente y está disponible en `/docs`
- Todos los endpoints incluyen validación de datos y mensajes de error descriptivos
- El sistema verifica automáticamente la disponibilidad de habitaciones antes de crear reservas
- Las reservas evitan solapamientos para la misma habitación en las mismas fechas

## 🎯 Versión MVP

Esta es una versión MVP (Minimum Viable Product) simplificada que incluye solo lo esencial:
- Una sola tabla de reservas
- Campos básicos: nombre de cliente, nombre de habitación, fechas, precio
- Validación de disponibilidad básica
- Gestión de estados de reserva

Para futuras versiones se pueden agregar:
- Tablas separadas de clientes y habitaciones
- Sistema de autenticación
- Reportes y estadísticas
- Integración con sistemas de pago

## 👥 Desarrollo

Este sistema fue desarrollado para el hotel Bosques de Chachagua utilizando FastAPI, SQLAlchemy y Pydantic.

## 📄 Licencia

Propietario - Bosques de Chachagua
