from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
from app.modulos.vehiculos.dominio.vehiculo import normalizar_placa



class ValidarReingreso:

    def __init__(self, sesion: Session):
        self.sesion = sesion

    def ejecutar(
        self,
        placa: str,
        sede_id: UUID,
    ) -> dict:

        placa_normalizada = normalizar_placa(placa)

        sede = self.sesion.get(SedeModelo, sede_id)

        if sede is None:
            raise ValueError("La sede no existe.")

        zona_horaria = ZoneInfo(sede.zona_horaria)

        ahora = datetime.now(zona_horaria)

        hora_inicio = sede.inicio_dia_operativo

        inicio_dia = ahora.replace(
            hour=hora_inicio.hour,
            minute=hora_inicio.minute,
            second=hora_inicio.second,
            microsecond=0,
        )

        if ahora < inicio_dia:
            dia_operativo = (ahora.date() - timedelta(days=1))
        else:
            dia_operativo = ahora.date()

        cobro = (
            self.sesion.query(CobroModelo)
            .filter(
                CobroModelo.placa == placa_normalizada,
                CobroModelo.sede_id == sede_id,
                CobroModelo.dia_operativo == dia_operativo,
            )
            .first()
        )

        if cobro is None:
            return {
                "autorizado": False,
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "dia_operativo": dia_operativo,
                "motivo": "No existe un cobro vigente para este vehículo.",
                "cobro_id": None,
            }

        pago = (
            self.sesion.query(PagoModelo)
            .filter(
                PagoModelo.cobro_id == cobro.id,
            )
            .first()
        )

        if pago is None:
            return {
                "autorizado": False,
                "placa": placa_normalizada,
                "sede_id": sede_id,
                "dia_operativo": dia_operativo,
                "motivo": "El cobro del día operativo está pendiente de pago.",
                "cobro_id": cobro.id,
            }

        return {
            "autorizado": True,
            "placa": placa_normalizada,
            "sede_id": sede_id,
            "dia_operativo": dia_operativo,
            "motivo": "Reingreso autorizado. El cobro del día operativo ya está pagado.",
            "cobro_id": cobro.id,
        }