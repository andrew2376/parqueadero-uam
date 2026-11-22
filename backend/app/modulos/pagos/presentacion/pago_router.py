from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.pagos.aplicacion.registrar_pago_efectivo import (
    RegistrarPagoEfectivo,
)
from app.modulos.pagos.infraestructura.pago_repositorio_sqlalchemy import (
    PagoRepositorioSQLAlchemy,
)
from app.modulos.pagos.presentacion.esquemas_pago import (
    PagoEfectivoCrear,
    PagoRespuesta,
)

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)


@router.post(
    "/efectivo",
    response_model=PagoRespuesta,
    status_code=status.HTTP_200_OK,
)
def registrar_pago_efectivo(
    datos: PagoEfectivoCrear,
    sesion: Session = Depends(obtener_sesion),
):
    repositorio = PagoRepositorioSQLAlchemy(sesion)

    caso_uso = RegistrarPagoEfectivo(
        repositorio=repositorio,
        sesion=sesion,
    )

    try:
        pago = caso_uso.ejecutar(
            cobro_id=datos.cobro_id,
            clave_idempotencia=datos.clave_idempotencia,
            valor=datos.valor,
        )

        return {
            "id": pago.id,
            "cobro_id": pago.cobro_id,
            "medio_pago": pago.medio_pago,
            "valor": pago.valor,
            "fecha_hora_pago": pago.fecha_hora_pago,
            "clave_idempotencia": pago.clave_idempotencia,
        }

    except ValueError as error:
        mensaje = str(error)

        if "no existe" in mensaje.lower():
            codigo = status.HTTP_404_NOT_FOUND
        elif "ya" in mensaje.lower() or "idempotencia" in mensaje.lower():
            codigo = status.HTTP_409_CONFLICT
        else:
            codigo = status.HTTP_422_UNPROCESSABLE_ENTITY

        raise HTTPException(
            status_code=codigo,
            detail=mensaje,
        )