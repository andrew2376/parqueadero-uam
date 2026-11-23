from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.cupos.dominio.cupo import Cupo


class CupoRepositorio(ABC):
    @abstractmethod
    def consultar_disponibilidad(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Cupo:
        pass

    @abstractmethod
    def reservar_cupo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Cupo:
        pass
