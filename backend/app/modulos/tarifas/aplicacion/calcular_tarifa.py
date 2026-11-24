
from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from app.modulos.tarifas.dominio.franja_horaria import (
    determinar_franja_horaria,
)
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class CalcularTarifa:
    """
    Caso de uso para calcular el valor de una tarifa
    según la sede, el vehículo y la versión vigente
    en la fecha de la operación.
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
        zona = ZoneInfo(zona_horaria)

        if fecha_hora.tzinfo is None or fecha_hora.utcoffset() is None:
            raise ValueError(
                "La fecha y hora del cálculo deben incluir zona horaria."
            )

        fecha_local = fecha_hora.astimezone(zona)

        tarifa = self.repositorio.buscar_vigente(
            sede_id,
            tipo_vehiculo,
            fecha_local,
        )

        if tarifa is None:
            raise ValueError(
                "No existe una tarifa vigente para este vehículo "
                "en la sede y fecha indicadas."
            )

        # No se valida tarifa.activa aquí:
        # una versión histórica puede estar inactiva y seguir siendo
        # válida para operaciones realizadas durante su vigencia.

        franja = determinar_franja_horaria(
            fecha_local,
            zona_horaria,
        )

        valor = tarifa.obtener_valor(franja)

        return {
            "sede_id": sede_id,
            "tarifa_id": tarifa.id,
            "version_tarifa": tarifa.version,
            "tipo_vehiculo": tarifa.tipo_vehiculo,
            "franja_horaria": franja.value,
            "tarifa_aplicada": (
                f"{tarifa.tipo_vehiculo}_{franja.value}_V{tarifa.version}"
            ),
            "valor_tarifa": valor,
            "fecha_hora": fecha_local,
        }
