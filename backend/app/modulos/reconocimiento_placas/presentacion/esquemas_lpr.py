from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, Field

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    OrigenEventoLectura,
)
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import (
    EstadoLectura,
    OrigenLectura,
)
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo, normalizar_placa


def normalizar_placa_textual(valor: object) -> object:
    return normalizar_placa(valor) if isinstance(valor, str) else valor


PlacaNormalizada = Annotated[str, BeforeValidator(normalizar_placa_textual)]


class ValidarLecturaManualSolicitud(BaseModel):
    carril_id: UUID
    placa_confirmada: PlacaNormalizada = Field(
        ...,
        min_length=5,
        max_length=6,
        description="Placa confirmada o corregida por el operador",
    )
    operador_id: str = Field(..., description="Identificador del operador que valida")
    placa_detectada_previa: str | None = Field(
        default=None,
        description="Placa que leyó la cámara originalmente",
    )
    confianza_previa: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Porcentaje de confianza previo",
    )
    umbral_confianza: float = Field(
        default=70.0,
        ge=0.0,
        le=100.0,
        description="Umbral de confianza configurado",
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


class LecturaManualSolicitud(BaseModel):
    carril_id: UUID
    placa: PlacaNormalizada = Field(
        ...,
        min_length=5,
        max_length=6,
        description="Placa ingresada manualmente",
    )


class EventoLecturaRespuesta(BaseModel):
    id: UUID
    sede_id: UUID
    carril_id: UUID
    placa: str | None
    confianza: float
    origen: OrigenEventoLectura
    estado: EstadoEventoLectura
    fecha_hora: datetime


class SimulacionLPRRespuesta(EventoLecturaRespuesta):
    tipo_vehiculo: TipoVehiculo | None
    requiere_confirmacion_manual: bool
