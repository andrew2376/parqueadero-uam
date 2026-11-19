
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.configuracion import obtener_configuracion
from app.infraestructura.base_datos.modelos import Base


# Configuración de Alembic
config = context.config

# Configurar los registros de actividad
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Obtener la configuración de la aplicación
configuracion = obtener_configuracion()

# Utilizar la URL de conexión definida en el archivo .env
config.set_main_option(
    "sqlalchemy.url",
    configuracion.url_base_datos.replace("%", "%%")
)

# Metadata de los modelos de SQLAlchemy
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Ejecutar migraciones sin establecer una conexión directa."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Ejecutar migraciones mediante una conexión a la base de datos."""

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
