from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.autenticacion.dominio.usuario import RolUsuario
from app.modulos.autenticacion.presentacion.dependencias_auth import requerir_rol
from app.modulos.carriles.dominio.carril import TipoCarril
from app.modulos.carriles.infraestructura.carril_repositorio_sqlalchemy import (
    CarrilRepositorioSQLAlchemy,
)
from app.modulos.eventos_lectura.aplicacion.registrar_evento_lectura import (
    RegistrarEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura import EventoLectura
from app.modulos.eventos_lectura.infraestructura.evento_lectura_repositorio_sqlalchemy import (
    EventoLecturaRepositorioSQLAlchemy,
)
from app.modulos.reconocimiento_placas.aplicacion.casos_uso_lpr import (
    RegistrarLecturaManual,
    SimularLecturaPlaca,
    ValidarLecturaBajaConfianza,
)
from app.modulos.reconocimiento_placas.aplicacion.registrar_evento_desde_lpr import (
    RegistrarEventoDesdeLPR,
)
from app.modulos.reconocimiento_placas.dominio.lector_lpr_puerto import LectorLPRPuerto
from app.modulos.reconocimiento_placas.dominio.lectura_lpr import LecturaLPR
from app.modulos.reconocimiento_placas.infraestructura.lector_lpr_simulado import (
    EscenarioSimulacion,
    LectorLPRSimulado,
)
from app.modulos.reconocimiento_placas.presentacion.esquemas_lpr import (
    EventoLecturaRespuesta,
    LecturaLPREsquema,
    LecturaManualSolicitud,
    SimulacionLPRRespuesta,
    ValidarLecturaManualSolicitud,
)

router = APIRouter(
    prefix="/lecturas-lpr",
    tags=["Reconocimiento de placas LPR"],
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


def capturar_y_registrar(
    carril_id: UUID, lector: LectorLPRPuerto, sesion: Session
) -> tuple[LecturaLPR, EventoLectura]:
    try:
        lectura = SimularLecturaPlaca(lector).ejecutar(carril_id)
        return lectura, construir_registrador_eventos(sesion).ejecutar(lectura)

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
    "/automatica",
    dependencies=[Depends(requerir_rol(RolUsuario.OPERADOR))],
    response_model=EventoLecturaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_lectura_automatica(
    carril_id: UUID,
    sesion: Session = Depends(obtener_sesion),
):
    _, evento = capturar_y_registrar(carril_id, LectorLPRSimulado(), sesion)
    return evento


@router.post(
    "/simulacion",
    dependencies=[Depends(requerir_rol(RolUsuario.OPERADOR))],
    response_model=SimulacionLPRRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def simular_lectura_de_entrada(
    carril_id: UUID,
    escenario: EscenarioSimulacion = EscenarioSimulacion.ALTA,
    sesion: Session = Depends(obtener_sesion),
) -> SimulacionLPRRespuesta:
    carril = CarrilRepositorioSQLAlchemy(sesion).obtener_por_id(carril_id)
    if carril is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El carril indicado no existe.")
    if not carril.activo or carril.tipo not in (TipoCarril.ENTRADA, TipoCarril.MIXTO):
        raise HTTPException(status.HTTP_409_CONFLICT, "El carril no está habilitado para ingreso.")

    lector = LectorLPRSimulado.para_escenario(escenario)
    lectura, evento = capturar_y_registrar(carril_id, lector, sesion)
    return SimulacionLPRRespuesta(
        **EventoLecturaRespuesta.model_validate(evento, from_attributes=True).model_dump(),
        tipo_vehiculo=lectura.tipo_vehiculo,
        requiere_confirmacion_manual=lectura.requiere_confirmacion_manual,
    )


@router.post(
    "/manual",
    dependencies=[Depends(requerir_rol(RolUsuario.OPERADOR))],
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
