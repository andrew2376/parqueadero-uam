from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.pagos.dominio.pago import Pago
from app.modulos.pagos.dominio.pago_repositorio import PagoRepositorio


class RegistrarPagoEfectivo:

    def __init__(
        self,
        repositorio: PagoRepositorio,
        sesion: Session,
    ):
        self.repositorio = repositorio
        self.sesion = sesion

    def ejecutar(
        self,
        cobro_id,
        clave_idempotencia: str,
        valor: Decimal,
    ) -> Pago:

        clave_idempotencia = clave_idempotencia.strip()

        if not clave_idempotencia:
            raise ValueError("La clave de idempotencia es obligatoria.")

        if valor <= 0:
            raise ValueError("El valor del pago debe ser mayor que cero.")

        # Si la misma solicitud ya fue procesada, devolver el pago existente.
        pago_existente = (
            self.repositorio.buscar_por_clave_idempotencia(
                clave_idempotencia
            )
        )

        if pago_existente is not None:
            if pago_existente.cobro_id != cobro_id:
                raise ValueError(
                    "La clave de idempotencia ya fue utilizada "
                    "para otro cobro."
                )

            return pago_existente

        # Verificar que el cobro exista.
        cobro = (
            self.sesion.query(CobroModelo)
            .filter(CobroModelo.id == cobro_id)
            .first()
        )

        if cobro is None:
            raise ValueError("El cobro no existe.")

        # Verificar que el cobro no esté pagado previamente.
        pago_previo = self.repositorio.buscar_por_cobro(cobro_id)

        if pago_previo is not None:
            raise ValueError("Este cobro ya se encuentra pagado.")

        # El pago debe corresponder al valor exacto del cobro.
        valor_cobro = Decimal(str(cobro.valor_tarifa))

        if valor != valor_cobro:
            raise ValueError(
                "El valor del pago no coincide con el valor del cobro."
            )

        pago = Pago(
            id=uuid4(),
            cobro_id=cobro_id,
            medio_pago="EFECTIVO",
            valor=valor,
            fecha_hora_pago=datetime.now().astimezone(),
            clave_idempotencia=clave_idempotencia,
        )

        try:
            return self.repositorio.guardar(pago)

        except IntegrityError:
            # Una petición concurrente pudo registrar el pago primero.
            self.sesion.rollback()

            pago_existente = (
                self.repositorio.buscar_por_clave_idempotencia(
                    clave_idempotencia
                )
            )

            if pago_existente is not None:
                if pago_existente.cobro_id == cobro_id:
                    return pago_existente

                raise ValueError(
                    "La clave de idempotencia ya fue utilizada."
                )

            pago_existente = self.repositorio.buscar_por_cobro(cobro_id)

            if pago_existente is not None:
                raise ValueError("Este cobro ya se encuentra pagado.")

            raise