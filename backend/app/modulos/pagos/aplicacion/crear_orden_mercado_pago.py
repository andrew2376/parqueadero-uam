from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.pagos.infraestructura.mercado_pago_cliente import (
    MercadoPagoCliente,
)
from app.modulos.pagos.infraestructura.orden_mercado_pago_modelo import (
    OrdenMercadoPagoModelo,
)
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo


class CrearOrdenMercadoPago:
    def __init__(
        self,
        sesion: Session,
        cliente: MercadoPagoCliente,
    ):
        self.sesion = sesion
        self.cliente = cliente

    def ejecutar(
        self,
        cobro_id: UUID,
        email: str,
        clave_idempotencia: str,
    ) -> dict:
        email = email.strip().lower()
        clave_idempotencia = clave_idempotencia.strip()

        if not email:
            raise ValueError("El correo electrónico es obligatorio.")

        if not clave_idempotencia:
            raise ValueError("La clave de idempotencia es obligatoria.")

        if len(clave_idempotencia) > 100:
            raise ValueError("La clave de idempotencia no puede superar 100 caracteres.")

        # Verificar que el cobro exista.
        cobro = self.sesion.query(CobroModelo).filter(CobroModelo.id == cobro_id).first()

        if cobro is None:
            raise ValueError("El cobro no existe.")

        # Verificar que el cobro no tenga un pago registrado.
        pago_existente = (
            self.sesion.query(PagoModelo).filter(PagoModelo.cobro_id == cobro_id).first()
        )

        if pago_existente is not None:
            raise ValueError("Este cobro ya se encuentra pagado.")

        # Buscar una orden anterior con la misma clave.
        orden = (
            self.sesion.query(OrdenMercadoPagoModelo)
            .filter(OrdenMercadoPagoModelo.clave_idempotencia == clave_idempotencia)
            .first()
        )

        if orden is not None:
            if orden.cobro_id != cobro_id:
                raise ValueError("La clave de idempotencia ya fue utilizada para otro cobro.")

            # Si ya tenemos el enlace, devolvemos la orden existente.
            if orden.checkout_url:
                return self._respuesta(orden)

            # Si no hay enlace, reutilizamos la orden y sus identificadores.
            # No creamos otra orden interna ni cambiamos la clave.
            valor = Decimal(str(orden.valor))
            external_reference = orden.external_reference

        else:
            valor = Decimal(str(cobro.valor_tarifa))

            if valor <= 0:
                raise ValueError("El valor del cobro debe ser mayor que cero.")

            # Crear identificadores internos.
            orden_id = uuid4()
            external_reference = str(orden_id)

            # Guardar primero la orden pendiente.
            orden = OrdenMercadoPagoModelo(
                id=orden_id,
                cobro_id=cobro.id,
                external_reference=external_reference,
                estado="CREATING",
                valor=valor,
                moneda="COP",
                clave_idempotencia=clave_idempotencia,
            )

            try:
                self.sesion.add(orden)
                self.sesion.commit()
                self.sesion.refresh(orden)

            except Exception:
                self.sesion.rollback()
                raise

        # Construir la solicitud para Mercado Pago.
        datos_orden = {
            "type": "online",
            "processing_mode": "manual",
            "total_amount": f"{valor:.2f}",
            "external_reference": external_reference,
            "description": f"Pago de parqueadero - Placa {cobro.placa}",
            "payer": {
                "email": email,
            },
            "items": [
                {
                    "title": f"Servicio de parqueadero - {cobro.placa}",
                    "quantity": 1,
                    "unit_price": f"{valor:.2f}",
                }
            ],
        }

        # Se conserva la misma clave de idempotencia en cada reintento.
        # Si hay un error de conexión, la orden queda pendiente para
        # permitir recuperar la respuesta sin crear otra orden.
        respuesta = self.cliente.crear_orden(
            datos=datos_orden,
            clave_idempotencia=clave_idempotencia,
        )

        proveedor_order_id = respuesta.get("id")
        checkout_url = respuesta.get("checkout_url")

        if not proveedor_order_id or not checkout_url:
            raise ValueError("Mercado Pago no devolvió el identificador o el enlace de checkout.")

        orden.proveedor_order_id = str(proveedor_order_id)
        orden.checkout_url = checkout_url
        orden.estado = respuesta.get("status", "CREATED")
        orden.estado_detalle = respuesta.get("status_detail")

        try:
            self.sesion.commit()
            self.sesion.refresh(orden)

        except Exception:
            self.sesion.rollback()
            raise

        return self._respuesta(orden)

    @staticmethod
    def _respuesta(orden: OrdenMercadoPagoModelo) -> dict:
        return {
            "orden_id": str(orden.id),
            "cobro_id": str(orden.cobro_id),
            "estado": orden.estado,
            "valor": str(orden.valor),
            "moneda": orden.moneda,
            "checkout_url": orden.checkout_url,
            "external_reference": orden.external_reference,
        }
