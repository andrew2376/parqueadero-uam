from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Estancia:
    id: UUID
    sede_id: UUID
    placa: str
    tipo_vehiculo: str
    fecha_hora_entrada: datetime
    fecha_hora_salida: datetime | None
    estado: str
