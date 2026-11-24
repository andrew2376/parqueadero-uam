from datetime import datetime
from uuid import UUID

from app.modulos.auditoria.dominio.auditoria import Auditoria
from app.modulos.auditoria.dominio.auditoria_repositorio import AuditoriaRepositorio


class ConsultarAuditoria:
    def __init__(self, repositorio: AuditoriaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        usuario_id: UUID | None = None,
        accion: str | None = None,
        entidad: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[Auditoria]:
        return self.repositorio.consultar(
            usuario_id=usuario_id,
            accion=accion,
            entidad=entidad,
            desde=desde,
            hasta=hasta,
            limite=limite,
        )
