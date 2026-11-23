from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.tarifas.dominio.tarifa import Tarifa


class TarifaRepositorio(ABC):
    @abstractmethod
    def guardar(self, tarifa: Tarifa) -> Tarifa:
        pass

    @abstractmethod
    def buscar_por_sede_y_tipo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Tarifa | None:
        pass

    @abstractmethod
    def listar_por_sede(self, sede_id: UUID) -> list[Tarifa]:
        pass
