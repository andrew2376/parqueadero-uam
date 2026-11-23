from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.configuracion import obtener_configuracion

# Obtener la configuración de la aplicación
configuracion = obtener_configuracion()


# Crear el motor de conexión a PostgreSQL
motor = create_engine(
    configuracion.url_base_datos,
    pool_pre_ping=True,
    echo=configuracion.entorno == "desarrollo",
)


# Crear el administrador de sesiones
FabricaSesiones = sessionmaker(
    bind=motor,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# Clase base para los modelos de SQLAlchemy
class Base(DeclarativeBase):
    pass


# Dependencia para obtener una sesión de base de datos
def obtener_sesion() -> Generator[Session, None, None]:
    sesion = FabricaSesiones()

    try:
        yield sesion
    finally:
        sesion.close()
