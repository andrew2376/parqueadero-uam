from uuid import UUID

from app.modulos.cupos.dominio.cupo import Cupo
from app.modulos.cupos.dominio.cupo_repositorio import CupoRepositorio


class ReservarCupo:
    def __init__(self, repositorio: CupoRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        tipo_vehiculo: str,
    ) -> Cupo:
        return self.repositorio.reservar_cupo(
            sede_id=sede_id,
            tipo_vehiculo=tipo_vehiculo,
        )
