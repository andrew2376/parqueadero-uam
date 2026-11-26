from collections.abc import Callable

from app.modulos.autenticacion.aplicacion.password_hasher import PasswordHasher
from app.modulos.autenticacion.dominio.usuario import Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio


class AutenticarUsuario:
    """Caso de uso para inicio de sesión."""

    def __init__(
        self,
        repositorio: UsuarioRepositorio,
        password_hasher: PasswordHasher,
        emitir_token: Callable[[Usuario], str],
    ) -> None:
        self.repositorio = repositorio
        self.password_hasher = password_hasher
        self.emitir_token = emitir_token

    def ejecutar(self, username: str, password_plano: str) -> tuple[str, Usuario]:
        usuario = self.repositorio.buscar_por_username(username)
        if (
            usuario is None
            or not usuario.activo
            or not self.password_hasher.verificar(password_plano, usuario.password_hash)
        ):
            raise ValueError("Credenciales inválidas o usuario inactivo.")

        return self.emitir_token(usuario), usuario
