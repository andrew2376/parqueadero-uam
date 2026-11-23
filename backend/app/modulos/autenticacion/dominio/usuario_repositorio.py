from abc import ABC, abstractmethod
from app.modulos.autenticacion.dominio.usuario import Usuario


class UsuarioRepositorio(ABC):
    @abstractmethod
    def buscar_por_username(self, username: str) -> Usuario | None:
        """Obtiene un usuario por su nombre de usuario único."""
        raise NotImplementedError
