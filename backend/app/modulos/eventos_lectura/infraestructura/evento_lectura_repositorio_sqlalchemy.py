from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    EventoLectura,
    OrigenEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura_repositorio import (
    EventoLecturaRepositorio,
)
from app.modulos.eventos_lectura.infraestructura.evento_lectura_modelo import (
    EventoLecturaModelo,
)


class EventoLecturaRepositorioSQLAlchemy(EventoLecturaRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, evento: EventoLectura) -> EventoLectura:
        modelo = EventoLecturaModelo(
            id=evento.id,
            sede_id=evento.sede_id,
            carril_id=evento.carril_id,
            fecha_hora=evento.fecha_hora.astimezone(UTC),
            placa=evento.placa,
            confianza=evento.confianza,
            origen=evento.origen.value,
            estado=evento.estado.value,
        )

        self.sesion.add(modelo)
        self.sesion.commit()
        self.sesion.refresh(modelo)

        return self._convertir_a_dominio(modelo)

    def obtener_por_id(self, evento_id: UUID) -> EventoLectura | None:
        modelo = self.sesion.get(EventoLecturaModelo, evento_id)

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def listar_por_sede(self, sede_id: UUID) -> list[EventoLectura]:
        consulta = (
            select(EventoLecturaModelo)
            .where(EventoLecturaModelo.sede_id == sede_id)
            .order_by(EventoLecturaModelo.fecha_hora.desc())
        )

        modelos = self.sesion.scalars(consulta).all()

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

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

        filtros = []

        if placa:
            filtros.append(
                EventoLecturaModelo.placa == placa.strip().upper()
            )

        if sede_id:
            filtros.append(EventoLecturaModelo.sede_id == sede_id)

        if estado:
            filtros.append(EventoLecturaModelo.estado == estado.value)

        if origen:
            filtros.append(EventoLecturaModelo.origen == origen.value)

        if fecha_desde:
            filtros.append(EventoLecturaModelo.fecha_hora >= fecha_desde)

        if fecha_hasta:
            filtros.append(EventoLecturaModelo.fecha_hora <= fecha_hasta)

        # Consultar el total de registros que cumplen los filtros
        consulta_total = select(
            func.count(EventoLecturaModelo.id)
        ).where(*filtros)

        total = self.sesion.scalar(consulta_total) or 0

        # Aplicar paginación
        desplazamiento = (pagina - 1) * limite

        consulta = (
            select(EventoLecturaModelo)
            .where(*filtros)
            .order_by(EventoLecturaModelo.fecha_hora.desc())
            .offset(desplazamiento)
            .limit(limite)
        )

        modelos = self.sesion.scalars(consulta).all()

        eventos = [
            self._convertir_a_dominio(modelo)
            for modelo in modelos
        ]

        return eventos, total

    @staticmethod
    def _convertir_a_dominio(
        modelo: EventoLecturaModelo,
    ) -> EventoLectura:
        fecha_hora = modelo.fecha_hora

        if fecha_hora.tzinfo is None:
            fecha_hora = fecha_hora.replace(tzinfo=UTC)

        return EventoLectura(
            id=modelo.id,
            sede_id=modelo.sede_id,
            carril_id=modelo.carril_id,
            fecha_hora=fecha_hora,
            placa=modelo.placa,
            confianza=float(modelo.confianza),
            origen=OrigenEventoLectura(modelo.origen),
            estado=EstadoEventoLectura(modelo.estado),
        )