"""
Sistema de Reservas - Bosques de Chachagua
API REST para gestión de reservas de hotel - MVP Simplificado
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import reservas
from app.database import engine, Base

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="Bosques de Chachagua - Sistema de Reservas",
    description="""
    API REST para la gestión de reservas del hotel Bosques de Chachagua (MVP).
    
    ## Características
    
    * **Gestión de Reservas**: Crear, consultar, actualizar y gestionar reservas
    * **Verificación de Disponibilidad**: Verifica automáticamente disponibilidad al crear reservas
    
    ## Documentación
    
    * **Swagger UI**: Disponible en `/docs`
    * **ReDoc**: Disponible en `/redoc`
    * **OpenAPI Schema**: Disponible en `/openapi.json`
    """,
    version="1.0.0",
    contact={
        "name": "Bosques de Chachagua",
        "email": "reservas@bosquesdechachagua.com",
    },
    license_info={
        "name": "Propietario",
    },
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir router de reservas
app.include_router(reservas.router, prefix="/api/v1", tags=["Reservas"])


@app.get("/", tags=["Inicio"])
async def root():
    """
    Endpoint raíz de la API
    
    Retorna información básica sobre el sistema de reservas
    """
    return {
        "mensaje": "Bienvenido al Sistema de Reservas - Bosques de Chachagua",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "reservas": "/api/v1/reservas"
        }
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de verificación de salud del sistema
    
    Útil para monitoreo y verificar que la API está funcionando
    """
    return {"status": "ok", "service": "Bosques de Chachagua API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
