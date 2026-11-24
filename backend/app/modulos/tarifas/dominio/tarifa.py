from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from app.modulos.tarifas.dominio.franja_horaria import FranjaHoraria


@dataclass
class Tarifa:
    """
    Entidad de dominio que representa una versión de la configuración
    tarifaria de un tipo de vehículo en una sede.
    """

    id: UUID
    sede_id: UUID
    tipo_vehiculo: str
    tarifa_diurna: Decimal
    tarifa_nocturna: Decimal
    activa: bool = True
    version: int = 1
    vigencia_desde: datetime = field(default_factory=lambda: datetime.now(UTC))
    vigencia_hasta: datetime | None = None

    def __post_init__(self):
        self.tipo_vehiculo = self.tipo_vehiculo.strip().upper()

        self.tarifa_diurna = Decimal(str(self.tarifa_diurna))
        self.tarifa_nocturna = Decimal(str(self.tarifa_nocturna))

        self._validar_valores()
        self._validar_reglas_negocio()
        self._validar_version()
        self._validar_vigencia()

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
        # RN-01: las motocicletas pueden tener ambas tarifas en cero.
        es_moto_gratuita = (
            self.tipo_vehiculo == "MOTO"
            and self.tarifa_diurna == Decimal("0")
            and self.tarifa_nocturna == Decimal("0")
        )

        if es_moto_gratuita:
            return

        # RN-02: la tarifa nocturna debe ser estrictamente menor
        # que la tarifa diurna.
        if self.tarifa_nocturna >= self.tarifa_diurna:
            raise ValueError(
                "La tarifa nocturna debe ser estrictamente menor que la tarifa diurna."
            )

    def _validar_version(self):
        if isinstance(self.version, bool) or not isinstance(self.version, int):
            raise ValueError("La versión debe ser un número entero.")

        if self.version < 1:
            raise ValueError("La versión debe ser mayor o igual a 1.")

    def _validar_vigencia(self):
        if not isinstance(self.vigencia_desde, datetime):
            raise ValueError("La fecha inicial de vigencia no es válida.")

        if self.vigencia_desde.tzinfo is None or self.vigencia_desde.utcoffset() is None:
            raise ValueError("La fecha inicial de vigencia debe incluir zona horaria.")

        if self.vigencia_hasta is not None:
            if not isinstance(self.vigencia_hasta, datetime):
                raise ValueError("La fecha final de vigencia no es válida.")

            if self.vigencia_hasta.tzinfo is None or self.vigencia_hasta.utcoffset() is None:
                raise ValueError("La fecha final de vigencia debe incluir zona horaria.")

            if self.vigencia_hasta <= self.vigencia_desde:
                raise ValueError("La fecha final debe ser posterior a la fecha inicial.")

    def obtener_valor(self, franja: FranjaHoraria) -> Decimal:
        """
        Obtiene el valor de la tarifa correspondiente a la franja horaria.
        """

        if franja == FranjaHoraria.DIURNA:
            return self.tarifa_diurna

        if franja == FranjaHoraria.NOCTURNA:
            return self.tarifa_nocturna

        raise ValueError("La franja horaria indicada no es válida.")
