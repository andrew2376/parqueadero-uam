from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.auditoria.dominio.auditoria import Auditoria
from app.modulos.auditoria.infraestructura.auditoria_repositorio_sqlalchemy import (
    AuditoriaRepositorioSQLAlchemy,
)
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.presentacion.dependencias_auth import requerir_rol
from app.modulos.carriles.aplicacion.casos_uso_carril import (
    ActualizarCarril,
    CambiarEstadoCarril,
    CrearCarril,
    ListarCarrilesPorSede,
    ObtenerCarril,
)
from app.modulos.carriles.infraestructura.carril_repositorio_sqlalchemy import (
    CarrilRepositorioSQLAlchemy,
)
from app.modulos.carriles.presentacion.esquemas_carril import (
    CarrilActualizar,
    CarrilCambiarEstado,
    CarrilCrear,
    CarrilRespuesta,
)

router = APIRouter(
    prefix="/carriles",
    tags=["Carriles"],
)


@router.post(
    "",
    response_model=CarrilRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_carril(
    datos: CarrilCrear,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = CarrilRepositorioSQLAlchemy(sesion)

    try:
        caso_uso = CrearCarril(repositorio)

        return caso_uso.ejecutar(
            sede_id=datos.sede_id,
            nombre=datos.nombre,
            tipo=datos.tipo,
        )

    except IntegrityError:
        sesion.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La sede no existe o ya tiene un carril con ese nombre.",
        ) from None


@router.get(
    "/sede/{sede_id}",
    response_model=list[CarrilRespuesta],
)
def listar_carriles_por_sede(
    sede_id: UUID,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = CarrilRepositorioSQLAlchemy(sesion)
    caso_uso = ListarCarrilesPorSede(repositorio)

    return caso_uso.ejecutar(sede_id)


@router.get(
    "/{carril_id}",
    response_model=CarrilRespuesta,
)
def obtener_carril(
    carril_id: UUID,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = CarrilRepositorioSQLAlchemy(sesion)
    caso_uso = ObtenerCarril(repositorio)

    carril = caso_uso.ejecutar(carril_id)

    if carril is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El carril no existe.",
        )

    return carril


@router.put(
    "/{carril_id}",
    response_model=CarrilRespuesta,
)
def actualizar_carril(
    carril_id: UUID,
    datos: CarrilActualizar,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = CarrilRepositorioSQLAlchemy(sesion)

    try:
        caso_uso = ActualizarCarril(repositorio)

        carril = caso_uso.ejecutar(
            carril_id=carril_id,
            nombre=datos.nombre,
            tipo=datos.tipo,
        )

        sesion.commit()

        return carril

    except ValueError as error:
        sesion.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IntegrityError:
        sesion.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un carril con ese nombre en la sede.",
        ) from None


@router.patch(
    "/{carril_id}/estado",
    response_model=CarrilRespuesta,
)
def cambiar_estado_carril(
    carril_id: UUID,
    datos: CarrilCambiarEstado,
    sesion: Session = Depends(obtener_sesion),
    usuario_actual: Usuario = Depends(requerir_rol(RolUsuario.ADMINISTRADOR)),
):
    repositorio_carril = CarrilRepositorioSQLAlchemy(sesion)
    repositorio_auditoria = AuditoriaRepositorioSQLAlchemy(sesion)

    caso_uso = CambiarEstadoCarril(repositorio_carril)

    try:
        # 1. Cambiar el estado del carril.
        carril = caso_uso.ejecutar(
            carril_id=carril_id,
            activo=datos.activo,
        )

        # 2. Crear el registro de auditoría.
        auditoria = Auditoria(
            usuario_id=usuario_actual.id,
            username=usuario_actual.username,
            accion="ACTIVAR_CARRIL" if datos.activo else "DESACTIVAR_CARRIL",
            entidad="CARRIL",
            entidad_id=str(carril.id),
            fecha_hora=datetime.now(UTC),
            detalles={
                "activo": carril.activo,
                "nombre_carril": carril.nombre,
                "tipo_carril": carril.tipo.value,
            },
        )

        # 3. Registrar auditoría sin confirmar todavía.
        repositorio_auditoria.registrar_sin_commit(auditoria)

        # 4. Confirmar conjuntamente el cambio y la auditoría.
        sesion.commit()

        return carril

    except ValueError as error:
        sesion.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except IntegrityError:
        sesion.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible completar el cambio de estado del carril.",
        ) from None

    except Exception:
        sesion.rollback()
        raise
