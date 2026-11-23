from datetime import date, datetime
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


class SalidaEstanciaSolicitud(BaseModel):
    sede_id: UUID
    placa: str = Field(
        min_length=5,
        max_length=10,
    )


class SalidaEstanciaRespuesta(BaseModel):
    autorizado: bool
    decision_barrera: str
    placa: str
    sede_id: UUID
    dia_operativo: date | None = None
    cobro_id: UUID | None = None
    estancia_id: UUID | None = None
    fecha_hora_salida: datetime | None = None
    motivo: str
