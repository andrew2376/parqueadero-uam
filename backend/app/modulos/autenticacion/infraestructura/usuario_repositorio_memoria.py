from collections.abc import Mapping

from app.modulos.autenticacion.aplicacion.password_hasher import PasswordHasher
from app.modulos.autenticacion.dominio.usuario import Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio
from app.modulos.autenticacion.infraestructura.usuarios_demo import USUARIOS_DEMO


class UsuarioRepositorioMemoria(UsuarioRepositorio):
    """Adaptador para pruebas y servidores aislados."""

    def __init__(self, password_hasher: PasswordHasher, passwords: Mapping[str, str]) -> None:
        self._usuarios = {
            demo.username: Usuario(
                id=demo.id,
                username=demo.username,
                nombre_completo=demo.nombre_completo,
                rol=demo.rol,
                password_hash=password_hasher.hashear(passwords[demo.username]),
            )
            for demo in USUARIOS_DEMO
        }

    def buscar_por_username(self, username: str) -> Usuario | None:
        return self._usuarios.get(username.strip().lower())
