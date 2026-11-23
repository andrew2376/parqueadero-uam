from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EventoLecturaRespuesta(BaseModel):
    id: UUID
    sede_id: UUID
    carril_id: UUID
    placa: str | None
    confianza: float
    origen: str
    estado: str
    fecha_hora: datetime


class EventosLecturaPaginadosRespuesta(BaseModel):
    items: list[EventoLecturaRespuesta]
    total: int
    pagina: int
    limite: int
    total_paginas: int