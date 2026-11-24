from uuid import UUID

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class ListarTarifas:
    """
    Caso de uso para consultar todas las tarifas
    y sus versiones registradas en una sede.
    """

    def __init__(self, repositorio: TarifaRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, sede_id: UUID) -> list[Tarifa]:
        return self.repositorio.listar_por_sede(sede_id)
