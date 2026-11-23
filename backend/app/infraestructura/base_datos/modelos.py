"""
Registro central de modelos SQLAlchemy.

Los modelos de infraestructura de cada módulo se importarán
aquí para que Alembic pueda detectarlos en las migraciones.
"""

from app.infraestructura.base_datos.conexion import Base  # noqa: F401
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo  # noqa: F401
from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo  # noqa: F401
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo  # noqa: F401
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo  # noqa: F401
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo  # noqa: F401