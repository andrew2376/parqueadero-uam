from sqlalchemy.orm import Session

from app.modulos.pagos.dominio.pago import Pago
from app.modulos.pagos.dominio.pago_repositorio import PagoRepositorio
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo


class PagoRepositorioSQLAlchemy(PagoRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def buscar_por_clave_idempotencia(
        self,
        clave_idempotencia: str,
    ) -> Pago | None:
        modelo = (
            self.sesion.query(PagoModelo)
            .filter(PagoModelo.clave_idempotencia == clave_idempotencia)
            .first()
        )

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def buscar_por_cobro(
        self,
        cobro_id,
    ) -> Pago | None:
        modelo = self.sesion.query(PagoModelo).filter(PagoModelo.cobro_id == cobro_id).first()

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def guardar(
        self,
        pago: Pago,
    ) -> Pago:
        modelo = PagoModelo(
            id=pago.id,
            cobro_id=pago.cobro_id,
            medio_pago=pago.medio_pago,
            valor=pago.valor,
            fecha_hora_pago=pago.fecha_hora_pago,
            clave_idempotencia=pago.clave_idempotencia,
        )

        self.sesion.add(modelo)
        self.sesion.commit()
        self.sesion.refresh(modelo)

        return self._convertir_a_dominio(modelo)

    @staticmethod
    def _convertir_a_dominio(
        modelo: PagoModelo,
    ) -> Pago:
        return Pago(
            id=modelo.id,
            cobro_id=modelo.cobro_id,
            medio_pago=modelo.medio_pago,
            valor=modelo.valor,
            fecha_hora_pago=modelo.fecha_hora_pago,
            clave_idempotencia=modelo.clave_idempotencia,
        )
