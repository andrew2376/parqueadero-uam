
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.tarifas.aplicacion.calcular_tarifa import CalcularTarifa
from app.modulos.tarifas.aplicacion.cerrar_vigencia import CerrarVigenciaTarifa
from app.modulos.tarifas.aplicacion.configurar_tarifa import ConfigurarTarifa
from app.modulos.tarifas.aplicacion.listar_tarifas import ListarTarifas
from app.modulos.tarifas.aplicacion.listar_versiones import ListarVersionesTarifa
from app.modulos.tarifas.infraestructura.tarifa_repositorio_sqlalchemy import (
    TarifaRepositorioSQLAlchemy,
)
from app.modulos.tarifas.presentacion.esquemas_tarifa import (
    TarifaCalculoRespuesta,
    TarifaCerrarVigencia,
    TarifaCrear,
    TarifaRespuesta,
)

router_tarifas = APIRouter(
    prefix="/tarifas",
    tags=["Tarifas"],
)


def obtener_repositorio(
    sesion: Session = Depends(obtener_sesion),
) -> TarifaRepositorioSQLAlchemy:
    return TarifaRepositorioSQLAlchemy(sesion)


@router_tarifas.post(
    "",
    response_model=TarifaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_tarifa(
    datos: TarifaCrear,
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = ConfigurarTarifa(repositorio)

        return caso_uso.ejecutar(
            sede_id=datos.sede_id,
            tipo_vehiculo=datos.tipo_vehiculo,
            tarifa_diurna=datos.tarifa_diurna,
            tarifa_nocturna=datos.tarifa_nocturna,
            vigencia_desde=datos.vigencia_desde,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible registrar la tarifa por un conflicto de datos.",
        ) from error


@router_tarifas.get(
    "/sede/{sede_id}",
    response_model=list[TarifaRespuesta],
)
def listar_tarifas_por_sede(
    sede_id: UUID,
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = ListarTarifas(repositorio)
        return caso_uso.ejecutar(sede_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router_tarifas.get(
    "/sede/{sede_id}/tipo/{tipo_vehiculo}/versiones",
    response_model=list[TarifaRespuesta],
)
def listar_versiones_tarifa(
    sede_id: UUID,
    tipo_vehiculo: str,
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = ListarVersionesTarifa(repositorio)

        return caso_uso.ejecutar(
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router_tarifas.get(
    "/vigente",
    response_model=TarifaCalculoRespuesta,
)
def consultar_tarifa_vigente(
    sede_id: UUID,
    tipo_vehiculo: str,
    fecha_hora: datetime,
    zona_horaria: str = "America/Bogota",
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = CalcularTarifa(repositorio)

        return caso_uso.ejecutar(
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
            fecha_hora=fecha_hora,
            zona_horaria=zona_horaria,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router_tarifas.patch(
    "/{tarifa_id}/vigencia",
    response_model=TarifaRespuesta,
)
def cerrar_vigencia_tarifa(
    tarifa_id: UUID,
    datos: TarifaCerrarVigencia,
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = CerrarVigenciaTarifa(repositorio)

        return caso_uso.ejecutar(
            tarifa_id=tarifa_id,
            fecha_fin=datos.vigencia_hasta,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router_tarifas.post(
    "/calcular",
    response_model=TarifaCalculoRespuesta,
)
def calcular_valor_tarifa(
    sede_id: UUID,
    tipo_vehiculo: str,
    fecha_hora: datetime,
    zona_horaria: str = "America/Bogota",
    repositorio: TarifaRepositorioSQLAlchemy = Depends(obtener_repositorio),
):
    try:
        caso_uso = CalcularTarifa(repositorio)

        return caso_uso.ejecutar(
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
            fecha_hora=fecha_hora,
            zona_horaria=zona_horaria,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
