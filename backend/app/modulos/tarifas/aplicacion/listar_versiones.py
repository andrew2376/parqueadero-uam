from uuid import UUID

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class ListarVersionesTarifa:
    """
    Caso de uso para consultar el historial de versiones
    de una tarifa por sede y tipo de vehículo.
    """

    def __init__(self, repositorio: TarifaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> list[Tarifa]:

        tipo_normalizado = tipo_vehiculo.strip().upper()

        if tipo_normalizado not in {"CARRO", "MOTO"}:
            raise ValueError("El tipo de vehículo debe ser CARRO o MOTO.")

        return self.repositorio.listar_versiones(
            sede_id,
            tipo_normalizado,
        )
