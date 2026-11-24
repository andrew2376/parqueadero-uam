from datetime import datetime
from uuid import UUID

from app.modulos.tarifas.dominio.tarifa import Tarifa
from app.modulos.tarifas.dominio.tarifa_repositorio import TarifaRepositorio


class CerrarVigenciaTarifa:
    """
    Caso de uso para finalizar la vigencia de una versión
    de tarifa sin eliminar su registro histórico.
    """

    def __init__(self, repositorio: TarifaRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        tarifa_id: UUID,
        fecha_fin: datetime,
    ) -> Tarifa:

        if fecha_fin.tzinfo is None or fecha_fin.utcoffset() is None:
            raise ValueError("La fecha final de vigencia debe incluir zona horaria.")

        return self.repositorio.cerrar_vigencia(
            tarifa_id,
            fecha_fin,
        )
