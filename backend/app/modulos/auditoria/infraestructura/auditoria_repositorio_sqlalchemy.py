from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.auditoria.dominio.auditoria import Auditoria
from app.modulos.auditoria.dominio.auditoria_repositorio import AuditoriaRepositorio
from app.modulos.auditoria.infraestructura.auditoria_modelo import AuditoriaModelo


class AuditoriaRepositorioSQLAlchemy(AuditoriaRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def registrar(self, auditoria: Auditoria) -> Auditoria:
        try:
            auditoria_registrada = self.registrar_sin_commit(auditoria)
            self.sesion.commit()
            return auditoria_registrada

        except Exception:
            self.sesion.rollback()
            raise

    def registrar_sin_commit(self, auditoria: Auditoria) -> Auditoria:
        modelo = AuditoriaModelo(
            id=auditoria.id,
            usuario_id=auditoria.usuario_id,
            username=auditoria.username,
            accion=auditoria.accion,
            entidad=auditoria.entidad,
            entidad_id=auditoria.entidad_id,
            fecha_hora=auditoria.fecha_hora,
            detalles=auditoria.detalles,
        )

        self.sesion.add(modelo)
        self.sesion.flush()

        return self._convertir_a_dominio(modelo)

    def consultar(
        self,
        usuario_id: UUID | None = None,
        accion: str | None = None,
        entidad: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        limite: int = 100,
    ) -> list[Auditoria]:
        consulta = self.sesion.query(AuditoriaModelo)

        if usuario_id is not None:
            consulta = consulta.filter(AuditoriaModelo.usuario_id == usuario_id)

        if accion is not None:
            consulta = consulta.filter(AuditoriaModelo.accion == accion)

        if entidad is not None:
            consulta = consulta.filter(AuditoriaModelo.entidad == entidad)

        if desde is not None:
            consulta = consulta.filter(AuditoriaModelo.fecha_hora >= desde)

        if hasta is not None:
            consulta = consulta.filter(AuditoriaModelo.fecha_hora <= hasta)

        limite_seguro = max(1, min(limite, 500))

        modelos = (
            consulta.order_by(AuditoriaModelo.fecha_hora.desc())
            .limit(limite_seguro)
            .all()
        )

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

    @staticmethod
    def _convertir_a_dominio(modelo: AuditoriaModelo) -> Auditoria:
        return Auditoria(
            id=modelo.id,
            usuario_id=modelo.usuario_id,
            username=modelo.username,
            accion=modelo.accion,
            entidad=modelo.entidad,
            entidad_id=modelo.entidad_id,
            fecha_hora=modelo.fecha_hora,
            detalles=modelo.detalles or {},
        )