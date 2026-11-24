from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Auditoria:
    usuario_id: UUID | None
    username: str
    accion: str
    entidad: str
    entidad_id: str
    fecha_hora: datetime = field(default_factory=lambda: datetime.now(UTC))
    detalles: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
