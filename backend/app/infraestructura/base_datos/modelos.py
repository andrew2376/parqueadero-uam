"""
Registro central de modelos SQLAlchemy.

Los modelos de infraestructura de cada módulo se importarán
aquí para que Alembic pueda detectarlos en las migraciones.
"""

from app.infraestructura.base_datos.conexion import Base

from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo
from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo