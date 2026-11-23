from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.carriles.dominio.carril import Carril


class CarrilRepositorio(ABC):
    @abstractmethod
    def guardar(self, carril: Carril) -> Carril:
        """Guarda un carril nuevo."""
        raise NotImplementedError

    @abstractmethod
    def obtener_por_id(self, carril_id: UUID) -> Carril | None:
        """Busca un carril por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_sede(self, sede_id: UUID) -> list[Carril]:
        """Lista los carriles asociados a una sede."""
        raise NotImplementedError

    @abstractmethod
    def actualizar(self, carril: Carril) -> Carril:
        """Actualiza la información de un carril."""
        raise NotImplementedError
