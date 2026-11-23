from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class RolUsuario(str, Enum):
    OPERADOR = "OPERADOR"
    ADMINISTRADOR = "ADMINISTRADOR"


@dataclass
class Usuario:
    username: str
    password_hash: str
    nombre_completo: str
    rol: RolUsuario
    activo: bool = True
    id: UUID = field(default_factory=uuid4)
    creado_en: datetime = field(default_factory=lambda: datetime.now(UTC))

    def tiene_rol(self, rol_requerido: RolUsuario) -> bool:
        if self.rol == RolUsuario.ADMINISTRADOR:
            return True
        return self.rol == rol_requerido
