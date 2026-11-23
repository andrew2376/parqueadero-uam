from uuid import UUID
from app.modulos.autenticacion.aplicacion.servicio_autenticacion import hashear_password
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio


class UsuarioRepositorioMemoria(UsuarioRepositorio):
    """
    Repositorio desacoplado con usuarios demo seguros institucionales UAM (S207).
    """

    def __init__(self) -> None:
        self._usuarios: dict[str, Usuario] = {}
        self._inicializar_usuarios_demo()

    def _inicializar_usuarios_demo(self) -> None:
        # 1. Operador de turno
        usr_operador = Usuario(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            username="operador1",
            password_hash=hashear_password("operador123"),
            nombre_completo="Operador de Turno UAM",
            rol=RolUsuario.OPERADOR,
            activo=True,
        )
        self._usuarios[usr_operador.username] = usr_operador

        # 2. Administrador del sistema
        usr_admin = Usuario(
            id=UUID("00000000-0000-0000-0000-000000000002"),
            username="admin",
            password_hash=hashear_password("admin123"),
            nombre_completo="Administrador de Parqueadero UAM",
            rol=RolUsuario.ADMINISTRADOR,
            activo=True,
        )
        self._usuarios[usr_admin.username] = usr_admin

    def buscar_por_username(self, username: str) -> Usuario | None:
        return self._usuarios.get(username.strip().lower())


_repositorio_singleton = UsuarioRepositorioMemoria()


def obtener_repositorio_usuario() -> UsuarioRepositorio:
    return _repositorio_singleton
