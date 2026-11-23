from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    EventoLectura,
    OrigenEventoLectura,
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

    @abstractmethod
    def listar_filtrado(
        self,
        placa: str | None = None,
        sede_id: UUID | None = None,
        estado: EstadoEventoLectura | None = None,
        origen: OrigenEventoLectura | None = None,
        fecha_desde: datetime | None = None,
        fecha_hasta: datetime | None = None,
        pagina: int = 1,
        limite: int = 20,
    ) -> tuple[list[EventoLectura], int]:
        """Consulta eventos con filtros y paginación."""
        raise NotImplementedError
