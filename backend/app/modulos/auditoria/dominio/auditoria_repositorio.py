from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modulos.auditoria.dominio.auditoria import Auditoria


class AuditoriaRepositorio(ABC):
    @abstractmethod
    def registrar(self, auditoria: Auditoria) -> Auditoria:
        pass

    @abstractmethod
    def registrar_sin_commit(self, auditoria: Auditoria) -> Auditoria:
        pass

    @abstractmethod
    def consultar(
        self,
        usuario_id: UUID | None = None,
        accion: str | None = None,
        entidad: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[Auditoria]:
        pass
