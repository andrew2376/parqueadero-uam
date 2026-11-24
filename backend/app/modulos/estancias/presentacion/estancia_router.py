from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.estancias.aplicacion.registrar_entrada import RegistrarEntrada
from app.modulos.estancias.aplicacion.registrar_salida import RegistrarSalida
from app.modulos.estancias.infraestructura.estancia_repositorio_sqlalchemy import (
    EstanciaRepositorioSQLAlchemy,
)
from app.modulos.estancias.presentacion.esquemas_estancia import (
    EntradaEstanciaCrear,
    EstanciaRespuesta,
    SalidaEstanciaRespuesta,
    SalidaEstanciaSolicitud,
)

router = APIRouter(
    prefix="/estancias",
    tags=["Estancias"],
)


@router.post(
    "/entrada",
    response_model=EstanciaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def registrar_entrada(
    datos: EntradaEstanciaCrear,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = EstanciaRepositorioSQLAlchemy(sesion)

    caso_uso = RegistrarEntrada(
        repositorio=repositorio,
        sesion=sesion,
    )

    try:
        estancia = caso_uso.ejecutar(
            placa=datos.placa,
            sede_id=datos.sede_id,
            tipo_vehiculo=datos.tipo_vehiculo,
        )

        return EstanciaRespuesta(
            id=estancia.id,
            sede_id=estancia.sede_id,
            placa=estancia.placa,
            tipo_vehiculo=estancia.tipo_vehiculo,
            fecha_hora_entrada=estancia.fecha_hora_entrada,
            fecha_hora_salida=estancia.fecha_hora_salida,
            estado=estancia.estado,
        )

    except ValueError as error:
        mensaje = str(error)
        mensaje_lower = mensaje.lower()

        if "activa" in mensaje_lower or "cupos disponibles" in mensaje_lower:
            codigo = status.HTTP_409_CONFLICT
        elif "no existe" in mensaje_lower:
            codigo = status.HTTP_404_NOT_FOUND
        else:
            codigo = status.HTTP_422_UNPROCESSABLE_ENTITY

        raise HTTPException(
            status_code=codigo,
            detail=mensaje,
        ) from error


@router.post(
    "/salida",
    response_model=SalidaEstanciaRespuesta,
    status_code=status.HTTP_200_OK,
)
def registrar_salida(
    datos: SalidaEstanciaSolicitud,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = EstanciaRepositorioSQLAlchemy(sesion)

    caso_uso = RegistrarSalida(
        repositorio=repositorio,
        sesion=sesion,
    )

    try:
        return caso_uso.ejecutar(
            placa=datos.placa,
            sede_id=datos.sede_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
