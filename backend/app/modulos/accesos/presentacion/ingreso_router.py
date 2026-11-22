from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.accesos.aplicacion.registrar_ingreso import RegistrarIngresoVehiculo
from app.modulos.accesos.infraestructura.acceso_repositorio_sqlalchemy import (
    AccesoRepositorioSQLAlchemy,
)
from app.modulos.accesos.presentacion.esquemas_ingreso import (
    RegistrarIngresoEsquema,
    ResultadoIngresoEsquema,
)

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
) -> ResultadoIngresoEsquema:
    repositorio = AccesoRepositorioSQLAlchemy(sesion)
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
