from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.accesos.aplicacion.registrar_ingreso import RegistrarIngresoVehiculo
from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.infraestructura.acceso_repositorio_memoria import (
    obtener_repositorio_acceso,
)
from app.modulos.accesos.presentacion.esquemas_ingreso import (
    RegistrarIngresoEsquema,
    ResultadoIngresoEsquema,
)
from app.modulos.carriles.dominio.carril import TipoCarril
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo

router = APIRouter(
    prefix="/accesos",
    tags=["Accesos e Ingreso"],
)


@router.post(
    "/ingreso",
    response_model=ResultadoIngresoEsquema,
    status_code=status.HTTP_200_OK,
)
def registrar_ingreso(
    datos: RegistrarIngresoEsquema,
    sesion: Session = Depends(obtener_sesion),
    repositorio: AccesoRepositorio = Depends(obtener_repositorio_acceso),
) -> ResultadoIngresoEsquema:
    carril = sesion.get(CarrilModelo, datos.carril_id, with_for_update=True)
    if (
        carril is None
        or carril.sede_id != datos.sede_id
        or not carril.activo
        or carril.tipo not in (TipoCarril.ENTRADA, TipoCarril.MIXTO)
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El carril no está habilitado para ingreso en esta sede.",
        )
    caso_uso = RegistrarIngresoVehiculo(repositorio=repositorio, sesion=sesion)

    resultado = caso_uso.ejecutar(
        sede_id=datos.sede_id,
        carril_id=datos.carril_id,
        placa_raw=datos.placa,
    )
    return ResultadoIngresoEsquema(
        autorizado=resultado.autorizado,
        decision_barrera=resultado.decision_barrera,
        mensaje=resultado.mensaje,
        placa=resultado.placa,
        tipo_vehiculo=resultado.tipo_vehiculo,
        es_reingreso=resultado.es_reingreso,
        cupos_disponibles_restantes=resultado.cupos_disponibles_restantes,
        acceso_id=resultado.acceso_id,
    )
