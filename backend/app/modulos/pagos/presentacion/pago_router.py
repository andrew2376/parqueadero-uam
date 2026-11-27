
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuracion import obtener_configuracion
from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo
from app.modulos.pagos.aplicacion.crear_orden_mercado_pago import (
    CrearOrdenMercadoPago,
)
from app.modulos.pagos.aplicacion.registrar_pago_efectivo import (
    RegistrarPagoEfectivo,
)
from app.modulos.pagos.infraestructura.mercado_pago_cliente import (
    MercadoPagoCliente,
    MercadoPagoError,
)
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo
from app.modulos.pagos.infraestructura.pago_repositorio_sqlalchemy import (
    PagoRepositorioSQLAlchemy,
)
from app.modulos.pagos.presentacion.esquemas_pago import (
    CobroConsultaRespuesta,
    OrdenMercadoPagoCrear,
    OrdenMercadoPagoRespuesta,
    PagoEfectivoCrear,
    PagoRespuesta,
)
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.tarifas.dominio.franja_horaria import calcular_dia_operativo
from app.modulos.vehiculos.dominio.vehiculo import normalizar_placa

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)


@router.get(
    "/cobros/consulta",
    response_model=CobroConsultaRespuesta,
)
def consultar_cobro(
    placa: str = Query(..., min_length=5, max_length=10),
    sesion: Session = Depends(obtener_sesion),
):
    # 1. Normalizar la placa.
    try:
        placa_normalizada = normalizar_placa(placa)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error

    # 2. Obtener la primera sede.
    sede = sesion.scalars(select(SedeModelo).limit(1)).first()

    if sede is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una sede registrada.",
        )

    # 3. Calcular el día operativo.
    ahora = datetime.now(ZoneInfo(sede.zona_horaria))

    dia_operativo = calcular_dia_operativo(
        fecha_hora=ahora,
        zona_horaria=sede.zona_horaria,
        inicio_dia_operativo=sede.inicio_dia_operativo,
    )

    # 4. Buscar el cobro existente.
    cobro = (
        sesion.query(CobroModelo)
        .filter(
            CobroModelo.placa == placa_normalizada,
            CobroModelo.sede_id == sede.id,
            CobroModelo.dia_operativo == dia_operativo,
        )
        .first()
    )

    if cobro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No se encontró un cobro para la placa "
                f"{placa_normalizada} en el día operativo actual."
            ),
        )

    # 5. Consultar si el cobro ya tiene un pago registrado.
    pago = (
        sesion.query(PagoModelo)
        .filter(PagoModelo.cobro_id == cobro.id)
        .first()
    )

    # 6. Consultar si el vehículo todavía está dentro de la sede.
    estancia_activa = (
        sesion.query(EstanciaModelo)
        .filter(
            EstanciaModelo.sede_id == sede.id,
            EstanciaModelo.placa == placa_normalizada,
            EstanciaModelo.estado == "DENTRO",
            EstanciaModelo.fecha_hora_salida.is_(None),
        )
        .first()
    )

    return CobroConsultaRespuesta(
        cobro_id=cobro.id,
        sede_id=sede.id,
        sede_nombre=sede.nombre,
        placa=cobro.placa,
        dia_operativo=cobro.dia_operativo,
        tarifa_aplicada=cobro.tarifa_aplicada,
        valor_tarifa=cobro.valor_tarifa,
        pagado=pago is not None,
        pago_id=pago.id if pago else None,
        fecha_hora_pago=pago.fecha_hora_pago if pago else None,
        vehiculo_dentro=estancia_activa is not None,
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
        ) from error


@router.post(
    "/mercado-pago/ordenes",
    response_model=OrdenMercadoPagoRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_orden_mercado_pago(
    datos: OrdenMercadoPagoCrear,
    sesion: Session = Depends(obtener_sesion),
):
    configuracion = obtener_configuracion()
    cliente = MercadoPagoCliente(configuracion)

    caso_uso = CrearOrdenMercadoPago(
        sesion=sesion,
        cliente=cliente,
    )

    try:
        return caso_uso.ejecutar(
            cobro_id=datos.cobro_id,
            email=datos.email,
            clave_idempotencia=datos.clave_idempotencia,
        )

    except MercadoPagoError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

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
        ) from error
