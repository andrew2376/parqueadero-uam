from fastapi import APIRouter, HTTPException, status

from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    ValidarLecturaBajaConfianza,
)
from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    LecturaLPREsquema,
    ValidarLecturaManualSolicitud,
)

router = APIRouter(
    prefix="/lpr",
    tags=["Reconocimiento de Placas (LPR)"],
)


@router.post(
    "/validar-manual",
    response_model=LecturaLPREsquema,
    status_code=status.HTTP_200_OK,
    summary="Validar y corregir lectura manual de baja confianza (S201)",
)
def validar_lectura_manual(
    datos: ValidarLecturaManualSolicitud,
) -> LecturaLPREsquema:
    caso_uso = ValidarLecturaBajaConfianza()

    try:
        resultado = caso_uso.ejecutar(
            carril_id=datos.carril_id,
            placa_confirmada=datos.placa_confirmada,
            operador_id=datos.operador_id,
            placa_detectada_previa=datos.placa_detectada_previa,
            confianza_previa=datos.confianza_previa,
            umbral_confianza=datos.umbral_confianza,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    return LecturaLPREsquema(
        id=resultado.id,
        carril_id=resultado.carril_id,
        placa=resultado.placa,
        confianza=resultado.confianza,
        origen=resultado.origen,
        estado=resultado.estado,
        tipo_vehiculo=resultado.tipo_vehiculo,
        placa_original_detectada=resultado.placa_original_detectada,
        operador_id=resultado.operador_id,
        requiere_confirmacion_manual=resultado.requiere_confirmacion_manual,
    )

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
