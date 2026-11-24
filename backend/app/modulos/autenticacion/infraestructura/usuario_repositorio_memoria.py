from uuid import UUID

from app.modulos.autenticacion.aplicacion.password_hasher import PasswordHasher
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio
from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import PasswordHasherArgon2


class UsuarioRepositorioMemoria(UsuarioRepositorio):
    """
    Repositorio desacoplado con usuarios demo seguros institucionales UAM (S207).
    """

    def __init__(self, password_hasher: PasswordHasher) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._inicializar_usuarios_demo(password_hasher)

    def _inicializar_usuarios_demo(self, password_hasher: PasswordHasher) -> None:
        # 1. Operador de turno
        usr_operador = Usuario(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            username="operador1",
            password_hash=password_hasher.hashear("operador123"),
            nombre_completo="Operador de Turno UAM",
            rol=RolUsuario.OPERADOR,
            activo=True,
        )
        self._usuarios[usr_operador.username] = usr_operador

        # 2. Administrador del sistema
        usr_admin = Usuario(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            username="admin",
            password_hash=password_hasher.hashear("admin123"),
            nombre_completo="Administrador de Parqueadero UAM",
            rol=RolUsuario.ADMINISTRADOR,
            activo=True,
        )
        self._usuarios[usr_admin.username] = usr_admin

    def buscar_por_username(self, username: str) -> Usuario | None:
        return self._usuarios.get(username.strip().lower())


_repositorio_singleton = UsuarioRepositorioMemoria(PasswordHasherArgon2())


def obtener_repositorio_usuario() -> UsuarioRepositorio:
    return _repositorio_singleton
