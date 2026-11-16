
from dataclasses import dataclass
from datetime import time
from uuid import UUID


@dataclass
class Sede:
    """
    Entidad de dominio que representa una sede del parqueadero.
    """

    id: UUID
    nombre: str
    zona_horaria: str
    inicio_dia_operativo: time
    cupos_carro: int
    cupos_moto: int
