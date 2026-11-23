
from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EventoLectura,
)


class EventoLecturaRepositorio(ABC):

    @abstractmethod
    def guardar(self, evento: EventoLectura) -> EventoLectura:
        """Persiste un nuevo evento de lectura."""
        raise NotImplementedError

    @abstractmethod
    def obtener_por_id(self, evento_id: UUID) -> EventoLectura | None:
        """Busca un evento por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_sede(self, sede_id: UUID) -> list[EventoLectura]:
        """Lista los eventos registrados en una sede."""
        raise NotImplementedError
