from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.eventos_lectura.aplicacion.consultar_eventos_filtrados import (
    ConsultarEventosFiltrados,
)
from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    OrigenEventoLectura,
)
from app.modulos.eventos_lectura.infraestructura.evento_lectura_repositorio_sqlalchemy import (
    EventoLecturaRepositorioSQLAlchemy,
)
from app.modulos.eventos_lectura.presentacion.esquemas_evento_lectura import (
    EventoLecturaRespuesta,
    EventosLecturaPaginadosRespuesta,
)

router = APIRouter(
    prefix="/eventos-lectura",
    tags=["Eventos de Lectura"],
)


@router.get(
    "",
    response_model=EventosLecturaPaginadosRespuesta,
)
def consultar_eventos(
    placa: str | None = Query(default=None),
    sede_id: UUID | None = Query(default=None),
    estado: EstadoEventoLectura | None = Query(default=None),
    origen: OrigenEventoLectura | None = Query(default=None),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    limite: int = Query(default=20, ge=1, le=100),
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = EventoLecturaRepositorioSQLAlchemy(sesion)

    caso_uso = ConsultarEventosFiltrados(
        repositorio=repositorio,
    )

    eventos, total = caso_uso.ejecutar(
        placa=placa,
        sede_id=sede_id,
        estado=estado,
        origen=origen,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        pagina=pagina,
        limite=limite,
    )

    total_paginas = (total + limite - 1) // limite

    return EventosLecturaPaginadosRespuesta(
        items=[
            EventoLecturaRespuesta(
                id=evento.id,
                sede_id=evento.sede_id,
                carril_id=evento.carril_id,
                placa=evento.placa,
                confianza=evento.confianza,
                origen=evento.origen.value,
                estado=evento.estado.value,
                fecha_hora=evento.fecha_hora,
            )
            for evento in eventos
        ],
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=total_paginas,
    )