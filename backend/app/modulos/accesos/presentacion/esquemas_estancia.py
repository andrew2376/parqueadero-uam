
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EntradaEstanciaCrear(BaseModel):
    sede_id: UUID
    placa: str = Field(
        min_length=5,
        max_length=10,
    )
    tipo_vehiculo: str = Field(
        min_length=3,
        max_length=20,
    )


class EstanciaRespuesta(BaseModel):
    id: UUID
    sede_id: UUID
    placa: str
    tipo_vehiculo: str
    fecha_hora_entrada: datetime
    fecha_hora_salida: datetime | None
    estado: str
