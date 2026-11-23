from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.modulos.tarifas.dominio.franja_horaria import FranjaHoraria


@dataclass
class Tarifa:
    """
    Entidad de dominio que representa la configuración tarifaria
    de un tipo de vehículo en una sede.
    """

    id: UUID
    sede_id: UUID
    tipo_vehiculo: str
    tarifa_diurna: Decimal
    tarifa_nocturna: Decimal
    activa: bool = True

    def __post_init__(self):
        self.tipo_vehiculo = self.tipo_vehiculo.strip().upper()

        self.tarifa_diurna = Decimal(str(self.tarifa_diurna))
        self.tarifa_nocturna = Decimal(str(self.tarifa_nocturna))

        self._validar_valores()
        self._validar_reglas_negocio()

    def _validar_valores(self):
        if self.tipo_vehiculo not in {"CARRO", "MOTO"}:
            raise ValueError("El tipo de vehículo debe ser CARRO o MOTO.")

        for nombre, valor in (
            ("diurna", self.tarifa_diurna),
            ("nocturna", self.tarifa_nocturna),
        ):
            if not valor.is_finite():
                raise ValueError(f"La tarifa {nombre} debe ser un valor finito.")

            if valor < Decimal("0"):
                raise ValueError(f"La tarifa {nombre} no puede ser negativa.")

    def _validar_reglas_negocio(self):
        # RN-01: las motocicletas pueden iniciar con ambas tarifas en cero.
        es_moto_gratuita = (
            self.tipo_vehiculo == "MOTO"
            and self.tarifa_diurna == Decimal("0")
            and self.tarifa_nocturna == Decimal("0")
        )

        if es_moto_gratuita:
            return

        # RN-05: la tarifa nocturna debe ser menor que la diurna.
        if self.tarifa_nocturna >= self.tarifa_diurna:
            raise ValueError(
                "La tarifa nocturna debe ser estrictamente menor que la tarifa diurna."
            )

    def obtener_valor(self, franja: FranjaHoraria) -> Decimal:
        """
        RN-02: obtiene el valor correspondiente a la franja horaria.
        """
        if franja == FranjaHoraria.DIURNA:
            return self.tarifa_diurna

        if franja == FranjaHoraria.NOCTURNA:
            return self.tarifa_nocturna

        raise ValueError("La franja horaria indicada no es válida.")
