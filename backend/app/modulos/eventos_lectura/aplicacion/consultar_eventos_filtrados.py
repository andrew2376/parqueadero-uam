from datetime import datetime
from uuid import UUID

from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    EventoLectura,
    OrigenEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura_repositorio import (
    EventoLecturaRepositorio,
)


class ConsultarEventosFiltrados:
    def __init__(self, repositorio: EventoLecturaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
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

        return self.repositorio.listar_filtrado(
            placa=placa,
            sede_id=sede_id,
            estado=estado,
            origen=origen,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            pagina=pagina,
            limite=limite,
        )
