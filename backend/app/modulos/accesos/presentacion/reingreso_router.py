from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.accesos.aplicacion.validar_reingreso import (
    ValidarReingreso,
)
from app.modulos.accesos.presentacion.esquemas_reingreso import (
    ReingresoRespuesta,
    ReingresoSolicitud,
)

router = APIRouter(
    prefix="/accesos",
    tags=["Accesos"],
)


@router.post(
    "/reingreso",
    response_model=ReingresoRespuesta,
    status_code=status.HTTP_200_OK,
)
def validar_reingreso(
    datos: ReingresoSolicitud,
    sesion: Session = Depends(obtener_sesion),
):
    caso_uso = ValidarReingreso(sesion)

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
