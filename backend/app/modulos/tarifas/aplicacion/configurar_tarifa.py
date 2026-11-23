from decimal import Decimal
from uuid import UUID, uuid4

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class ConfigurarTarifa:
    """
    Caso de uso para crear o actualizar la tarifa
    de un tipo de vehículo en una sede.
    """

    def __init__(self, repositorio: TarifaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
        tarifa_diurna: Decimal,
        tarifa_nocturna: Decimal,
    ) -> Tarifa:

        tarifa = Tarifa(
            id=uuid4(),
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
            tarifa_diurna=tarifa_diurna,
            tarifa_nocturna=tarifa_nocturna,
            activa=True,
        )

        return self.repositorio.guardar(tarifa)
