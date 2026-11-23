from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    OrigenEventoLectura,
)


class LecturaManualSolicitud(BaseModel):
    carril_id: UUID
    placa: str = Field(min_length=1, max_length=10)


class EventoLecturaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sede_id: UUID
    carril_id: UUID
    fecha_hora: datetime
    placa: str | None
    confianza: float
    origen: OrigenEventoLectura
    estado: EstadoEventoLectura
