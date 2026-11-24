from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Cupo:
    """
    Representa la capacidad y disponibilidad de un tipo
    de vehículo dentro de una sede.
    """

    sede_id: UUID
    tipo_vehiculo: str
    capacidad: int
    ocupados: int

    def __post_init__(self):
        tipo = self.tipo_vehiculo.strip().upper()
        object.__setattr__(self, "tipo_vehiculo", tipo)

        if tipo not in {"CARRO", "MOTO"}:
            raise ValueError("El tipo de vehículo debe ser CARRO o MOTO.")

        if self.capacidad < 0:
            raise ValueError("La capacidad no puede ser negativa.")

        if self.ocupados < 0:
            raise ValueError("La ocupación no puede ser negativa.")

        if self.ocupados > self.capacidad:
            raise ValueError("La ocupación no puede superar la capacidad.")

    @property
    def disponibles(self) -> int:
        return self.capacidad - self.ocupados

    @property
    def esta_lleno(self) -> bool:
        return self.disponibles == 0

    @property
    def tiene_disponibilidad(self) -> bool:
        return self.disponibles > 0
