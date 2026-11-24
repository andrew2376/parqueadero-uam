from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modulos.tarifas.dominio.tarifa import Tarifa


class TarifaRepositorio(ABC):
    """
    Puerto de dominio para la persistencia y consulta
    de tarifas versionadas.
    """

    @abstractmethod
    def guardar(self, tarifa: Tarifa) -> Tarifa:
        """
        Guarda una nueva versión de tarifa.
        No debe sobrescribir versiones anteriores.
        """
        pass

    @abstractmethod
    def buscar_por_sede_y_tipo(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Tarifa | None:
        """
        Busca la versión activa más reciente de una tarifa.
        """
        pass

    @abstractmethod
    def buscar_vigente(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
        fecha: datetime,
    ) -> Tarifa | None:
        """
        Busca la tarifa vigente para una fecha determinada.
        """
        pass

    @abstractmethod
    def listar_por_sede(self, sede_id: UUID) -> list[Tarifa]:
        """
        Lista las tarifas de una sede.
        """
        pass

    @abstractmethod
    def listar_versiones(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> list[Tarifa]:
        """
        Obtiene el historial de versiones de una tarifa.
        """
        pass

    @abstractmethod
    def cerrar_vigencia(
        self,
        tarifa_id: UUID,
        fecha_fin: datetime,
    ) -> Tarifa:
        """
        Establece la fecha final de vigencia de una versión.
        """
        pass
