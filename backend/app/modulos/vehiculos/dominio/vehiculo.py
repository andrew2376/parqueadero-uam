import re
from dataclasses import dataclass
from enum import Enum


class TipoVehiculo(str, Enum):
    CARRO = "CARRO"
    MOTO = "MOTO"


def normalizar_placa(placa_raw: str) -> str:
    """
    Normaliza la placa eliminando espacios, guiones y convirtiéndola a mayúsculas.
    """
    if not placa_raw:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", placa_raw).upper()


def clasificar_placa(placa_raw: str) -> TipoVehiculo:
    """
    Clasifica una placa según las reglas colombianas (RN-01):
    - Carro: 3 letras y 3 números (ej. AAA123)
    - Moto: 3 letras, 2 números y 1 letra (ej. AAA12A)

    Lanza ValueError si el formato no es válido o está vacía.
    """
    placa = normalizar_placa(placa_raw)

    if not placa:
        raise ValueError("La placa no puede estar vacía.")

    # Formato Carro: AAA123 (3 letras seguidas de 3 dígitos)
    if re.fullmatch(r"^[A-Z]{3}\d{3}$", placa):
        return TipoVehiculo.CARRO

    # Formato Moto: AAA12A (3 letras, 2 dígitos, 1 letra)
    if re.fullmatch(r"^[A-Z]{3}\d{2}[A-Z]$", placa):
        return TipoVehiculo.MOTO

    raise ValueError(
        f"La placa '{placa_raw}' no cumple con el formato colombiano válido (AAA123 para carro o AAA12A para moto)."
    )


@dataclass
class Vehiculo:
    placa: str
    tipo: TipoVehiculo

    def __post_init__(self) -> None:
        self.placa = normalizar_placa(self.placa)
        tipo_calculado = clasificar_placa(self.placa)
        if self.tipo != tipo_calculado:
            raise ValueError(
                f"El tipo de vehículo especificado ({self.tipo}) no coincide con el calculado por la placa ({tipo_calculado})."
            )

    @classmethod
    def crear_desde_placa(cls, placa_raw: str) -> "Vehiculo":
        placa = normalizar_placa(placa_raw)
        tipo = clasificar_placa(placa)
        return cls(placa=placa, tipo=tipo)
