from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio
from app.modulos.autenticacion.infraestructura.usuario_modelo import UsuarioModelo


class UsuarioRepositorioSQLAlchemy(UsuarioRepositorio):
    def __init__(self, sesion: Session) -> None:
        self.sesion = sesion

    def buscar_por_username(self, username: str) -> Usuario | None:
        consulta = select(UsuarioModelo).where(UsuarioModelo.username == username.strip().lower())
        modelo = self.sesion.scalars(consulta).one_or_none()
        if modelo is None:
            return None

        return Usuario(
            id=modelo.id,
            username=modelo.username,
            password_hash=modelo.password_hash,
            nombre_completo=modelo.nombre_completo,
            rol=RolUsuario(modelo.rol),
            activo=modelo.activo,
            creado_en=modelo.creado_en,
        )
