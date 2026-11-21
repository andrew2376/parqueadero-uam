from abc import ABC, abstractmethod

from app.modulos.vehiculos.dominio.vehiculo import Vehiculo


class VehiculoRepositorio(ABC):

    @abstractmethod
    def buscar_por_placa(self, placa: str) -> Vehiculo | None:
        """Busca un vehículo previamente registrado por su placa."""
        raise NotImplementedError

    @abstractmethod
    def guardar(self, vehiculo: Vehiculo) -> Vehiculo:
        """Guarda o actualiza un vehículo."""
        raise NotImplementedError
