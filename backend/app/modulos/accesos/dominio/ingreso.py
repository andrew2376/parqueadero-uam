from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class EstadoAcceso(str, Enum):
    ACTIVO = "ACTIVO"      # Vehículo dentro del parqueadero
    FINALIZADO = "FINALIZADO"  # Vehículo salió del parqueadero


class DecisionBarrera(str, Enum):
    ABRIR = "ABRIR"
    MANTENER_CERRADA = "MANTENER_CERRADA"


@dataclass
class RegistroIngreso:
    """
    Entidad de dominio que representa el ingreso de un vehículo al parqueadero.
    """
    sede_id: UUID
    carril_id: UUID
    placa: str
    tipo_vehiculo: TipoVehiculo
    id: UUID = field(default_factory=uuid4)
    fecha_ingreso: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    estado: EstadoAcceso = EstadoAcceso.ACTIVO
    fecha_salida: datetime | None = None
    es_reingreso: bool = False

    def registrar_salida(self, fecha: datetime | None = None) -> None:
        if self.estado == EstadoAcceso.FINALIZADO:
            raise ValueError("El acceso ya se encuentra finalizado.")
        self.estado = EstadoAcceso.FINALIZADO
        self.fecha_salida = fecha or datetime.now(UTC)


@dataclass
class ResultadoIngreso:
    """
    Resultado de la evaluación y registro del intento de ingreso.
    """
    autorizado: bool
    decision_barrera: DecisionBarrera
    mensaje: str
    placa: str
    tipo_vehiculo: TipoVehiculo | None = None
    es_reingreso: bool = False
    cupos_disponibles_restantes: int | None = None
    acceso_id: UUID | None = None
