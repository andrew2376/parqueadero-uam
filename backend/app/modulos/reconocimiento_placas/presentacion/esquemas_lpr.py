from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    EstadoLectura,
    OrigenLectura,
)
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class ValidarLecturaManualSolicitud(BaseModel):
    carril_id: UUID
    placa_confirmada: str = Field(
        ...,
        min_length=5,
        max_length=6,
        description="Placa confirmada o corregida por el operador"
    )
    operador_id: str = Field(..., description="Identificador del operador que valida")
    placa_detectada_previa: str | None = Field(
        default=None,
        description="Placa que leyó la cámara originalmente"
    )
    confianza_previa: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Porcentaje de confianza previo"
    )
    umbral_confianza: float = Field(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Umbral de confianza configurado"
    )


class LecturaLPREsquema(BaseModel):
    id: UUID
    carril_id: UUID
    placa: str
    confianza: float
    origen: OrigenLectura
    estado: EstadoLectura
    tipo_vehiculo: TipoVehiculo | None = None
    placa_original_detectada: str | None = None
    operador_id: str | None = None
    requiere_confirmacion_manual: bool
