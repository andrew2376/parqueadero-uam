from uuid import UUID

from pydantic import BaseModel, Field

from app.modulos.accesos.dominio.ingreso import DecisionBarrera
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class RegistrarIngresoEsquema(BaseModel):
    sede_id: UUID
    carril_id: UUID
    placa: str = Field(..., min_length=3, max_length=10, description="Placa del vehículo a ingresar")


class ResultadoIngresoEsquema(BaseModel):
    autorizado: bool
    decision_barrera: DecisionBarrera
    mensaje: str
    placa: str
    tipo_vehiculo: TipoVehiculo | None = None
    es_reingreso: bool = False
    cupos_disponibles_restantes: int | None = None
    acceso_id: UUID | None = None
