from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class TipoCarril(str, Enum):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    MIXTO = "MIXTO"


@dataclass
class Carril:
    id: UUID
    sede_id: UUID
    nombre: str
    tipo: TipoCarril
    activo: bool = True

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()

        if not self.nombre:
            raise ValueError("El nombre del carril es obligatorio.")

        if len(self.nombre) > 80:
            raise ValueError("El nombre del carril no puede superar los 80 caracteres.")

    def desactivar(self) -> None:
        self.activo = False

    def activar(self) -> None:
        self.activo = True
