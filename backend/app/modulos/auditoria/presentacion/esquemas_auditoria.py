from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditoriaRespuesta(BaseModel):
    id: UUID
    usuario_id: UUID | None
    username: str
    accion: str
    entidad: str
    entidad_id: str
    fecha_hora: datetime
    detalles: dict
    