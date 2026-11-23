from abc import ABC, abstractmethod
from uuid import UUID

from app.modulos.accesos.dominio.ingreso import RegistroIngreso
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class AccesoRepositorio(ABC):

    @abstractmethod
    def guardar_ingreso(self, ingreso: RegistroIngreso) -> RegistroIngreso:
        """Guarda o actualiza un registro de ingreso."""
        raise NotImplementedError

    @abstractmethod
    def buscar_ingreso_activo_por_placa(self, placa: str, sede_id: UUID) -> RegistroIngreso | None:
        """Busca si el vehículo ya se encuentra dentro de la sede sin registrar salida (Anti-passback)."""
        raise NotImplementedError

    @abstractmethod
    def contar_vehiculos_activos(self, sede_id: UUID, tipo_vehiculo: TipoVehiculo) -> int:
        """Cuenta cuántos vehículos de cierto tipo se encuentran actualmente dentro de la sede."""
        raise NotImplementedError
