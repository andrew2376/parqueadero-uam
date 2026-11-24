from datetime import date, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
from app.modulos.tarifas.aplicacion.calcular_tarifa import CalcularTarifa
from app.modulos.tarifas.infraestructura.tarifa_repositorio_sqlalchemy import (
    TarifaRepositorioSQLAlchemy,
)


class GenerarCobro:
    def __init__(self, sesion: Session):
        self.sesion = sesion
        self.calculador = CalcularTarifa(TarifaRepositorioSQLAlchemy(sesion))

    def ejecutar(
        self,
        placa: str,
        sede_id: UUID,
        tipo_vehiculo: str,
        dia_operativo: date,
        fecha_hora: datetime,
        zona_horaria: str,
    ) -> CobroModelo:

        cobro_existente = (
            self.sesion.query(CobroModelo)
            .filter(
                CobroModelo.placa == placa,
                CobroModelo.sede_id == sede_id,
                CobroModelo.dia_operativo == dia_operativo,
            )
            .with_for_update()
            .first()
        )

        if cobro_existente is not None:
            return cobro_existente

        resultado = self.calculador.ejecutar(
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
            fecha_hora=fecha_hora,
            zona_horaria=zona_horaria,
        )

        cobro = CobroModelo(
            sede_id=sede_id,
            tarifa_id=resultado["tarifa_id"],
            version_tarifa=resultado["version_tarifa"],
            placa=placa,
            dia_operativo=dia_operativo,
            tarifa_aplicada=resultado["tarifa_aplicada"],
            valor_tarifa=resultado["valor_tarifa"],
            fecha_hora_generacion=resultado["fecha_hora"],
        )

        self.sesion.add(cobro)
        self.sesion.flush()

        return cobro
