from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class ReingresoSolicitud(BaseModel):
    placa: str = Field(min_length=5, max_length=10)
    sede_id: UUID


class ReingresoRespuesta(BaseModel):
    autorizado: bool
    placa: str
    sede_id: UUID
    dia_operativo: date
    motivo: str
    cobro_id: UUID | None