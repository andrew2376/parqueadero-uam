from dataclasses import dataclass
from uuid import UUID

from app.modulos.autenticacion.dominio.usuario import RolUsuario


@dataclass(frozen=True)
class UsuarioDemo:
    id: UUID
    username: str
    nombre_completo: str
    rol: RolUsuario


USUARIOS_DEMO = (
    UsuarioDemo(
        UUID("00000000-0000-0000-0000-000000000001"),
        "operador1",
        "Operador de Turno UAM",
        RolUsuario.OPERADOR,
    ),
    UsuarioDemo(
        UUID("00000000-0000-0000-0000-000000000002"),
        "admin",
        "Administrador de Parqueadero UAM",
        RolUsuario.ADMINISTRADOR,
    ),
)
