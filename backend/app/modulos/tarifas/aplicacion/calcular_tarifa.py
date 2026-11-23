from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from app.modulos.tarifas.dominio.franja_horaria import (
    determinar_franja_horaria,
)
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class CalcularTarifa:
    """
    Caso de uso para obtener el valor tarifario
    según la sede, el vehículo y la franja horaria.
    """

    def __init__(self, repositorio: TarifaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
        fecha_hora: datetime,
        zona_horaria: str,
    ) -> dict:

        tarifa = self.repositorio.buscar_por_sede_y_tipo(
            sede_id,
            tipo_vehiculo,
        )

        if tarifa is None:
            raise ValueError("No existe una tarifa configurada para este vehículo en la sede.")

        if not tarifa.activa:
            raise ValueError("La tarifa configurada se encuentra inactiva.")

        franja = determinar_franja_horaria(
            fecha_hora,
            zona_horaria,
        )

        valor = tarifa.obtener_valor(franja)

        return {
            "sede_id": sede_id,
            "tipo_vehiculo": tarifa.tipo_vehiculo,
            "franja_horaria": franja.value,
            "valor_tarifa": valor,
            "fecha_hora": fecha_hora.astimezone(ZoneInfo(zona_horaria)),
        }
