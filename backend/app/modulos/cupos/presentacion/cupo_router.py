from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.presentacion.dependencias_auth import requerir_rol
from app.modulos.cupos.aplicacion.actualizar_capacidades import ActualizarCapacidades
from app.modulos.cupos.aplicacion.consultar_disponibilidad import ConsultarDisponibilidad
from app.modulos.cupos.infraestructura.cupo_repositorio_sqlalchemy import (
    CupoRepositorioSQLAlchemy,
)
from app.modulos.cupos.presentacion.esquemas_cupo import (
    CapacidadesActualizar,
    CapacidadesRespuesta,
    CupoRespuesta,
)

router = APIRouter(
    prefix="/cupos",
    tags=["Cupos"],
)


@router.get(
    "/sede/{sede_id}",
    response_model=list[CupoRespuesta],
)
def consultar_cupos(
    sede_id: UUID,
    sesion: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(requerir_rol(RolUsuario.ADMINISTRADOR)),
):
    repositorio = CupoRepositorioSQLAlchemy(sesion)
    caso_uso = ConsultarDisponibilidad(repositorio)

    try:
        carros = caso_uso.ejecutar(sede_id, "CARRO")
        motos = caso_uso.ejecutar(sede_id, "MOTO")

        return [
            CupoRespuesta(
                sede_id=carros.sede_id,
                tipo_vehiculo=carros.tipo_vehiculo,
                capacidad=carros.capacidad,
                ocupados=carros.ocupados,
                disponibles=carros.disponibles,
            ),
            CupoRespuesta(
                sede_id=motos.sede_id,
                tipo_vehiculo=motos.tipo_vehiculo,
                capacidad=motos.capacidad,
                ocupados=motos.ocupados,
                disponibles=motos.disponibles,
            ),
        ]

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.put(
    "/sede/{sede_id}",
    response_model=CapacidadesRespuesta,
)
def actualizar_cupos(
    sede_id: UUID,
    datos: CapacidadesActualizar,
    sesion: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(requerir_rol(RolUsuario.ADMINISTRADOR)),
):
    repositorio = CupoRepositorioSQLAlchemy(sesion)
    caso_uso = ActualizarCapacidades(repositorio)

    try:
        cupos_carro, cupos_moto = caso_uso.ejecutar(
            sede_id=sede_id,
            cupos_carro=datos.cupos_carro,
            cupos_moto=datos.cupos_moto,
        )

        sesion.commit()

        return CapacidadesRespuesta(
            sede_id=sede_id,
            cupos_carro=cupos_carro,
            cupos_moto=cupos_moto,
        )

    except ValueError as error:
        sesion.rollback()

        codigo = (
            status.HTTP_404_NOT_FOUND
            if "no existe" in str(error).lower()
            else status.HTTP_409_CONFLICT
        )

        raise HTTPException(
            status_code=codigo,
            detail=str(error),
        ) from error

    except Exception:
        sesion.rollback()
        raise
