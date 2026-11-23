
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion

from app.modulos.carriles.infraestructura.carril_repositorio_sqlalchemy import (
    CarrilRepositorioSQLAlchemy,
)

from app.modulos.eventos_lectura.aplicacion.registrar_evento_lectura import (
    RegistrarEventoLectura,
)

from app.modulos.eventos_lectura.infraestructura.evento_lectura_repositorio_sqlalchemy import (
    EventoLecturaRepositorioSQLAlchemy,
)

from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    RegistrarLecturaManual,
    SimularLecturaPlaca,
)

from app.modulos.reconocimiento_placas.aplicacion.registrar_evento_desde_lpr import (
    RegistrarEventoDesdeLPR,
)

from app.modulos.reconocimiento_placas.infraestructura.lector_lpr_simulado import (
    LectorLPRSimulado,
)

from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    EventoLecturaRespuesta,
    LecturaManualSolicitud,
)


router = APIRouter(
    prefix="/lecturas-lpr",
    tags=["Reconocimiento de placas LPR"],
)


def construir_registrador_eventos(sesion: Session):
    carriles = CarrilRepositorioSQLAlchemy(sesion)
    eventos = EventoLecturaRepositorioSQLAlchemy(sesion)

    registrar_evento = RegistrarEventoLectura(
        eventos=eventos,
        carriles=carriles,
    )

    return RegistrarEventoDesdeLPR(
        carriles=carriles,
        registrar_evento=registrar_evento,
    )


@router.post(
    "/automatica",
    response_model=EventoLecturaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_lectura_automatica(
    carril_id: UUID,
    sesion: Session = Depends(obtener_sesion),
):
    try:
        lector = LectorLPRSimulado()

        caso_uso_lectura = SimularLecturaPlaca(lector)
        lectura = caso_uso_lectura.ejecutar(carril_id)

        registrar_evento = construir_registrador_eventos(sesion)
        evento = registrar_evento.ejecutar(lectura)

        return evento

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IntegrityError:
        sesion.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar el evento de lectura.",
        ) from None


@router.post(
    "/manual",
    response_model=EventoLecturaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_lectura_manual(
    datos: LecturaManualSolicitud,
    sesion: Session = Depends(obtener_sesion),
):
    try:
        caso_uso_lectura = RegistrarLecturaManual()

        lectura = caso_uso_lectura.ejecutar(
            carril_id=datos.carril_id,
            placa=datos.placa,
        )

        registrar_evento = construir_registrador_eventos(sesion)
        evento = registrar_evento.ejecutar(lectura)

        return evento

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IntegrityError:
        sesion.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar el evento de lectura.",
        ) from None
