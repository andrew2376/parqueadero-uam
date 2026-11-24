
from uuid import UUID

from app.modulos.cupos.dominio.cupo_repositorio import CupoRepositorio


class ActualizarCapacidades:

    def __init__(self, repositorio: CupoRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        cupos_carro: int,
        cupos_moto: int,
    ) -> tuple[int, int]:

        if cupos_carro < 0 or cupos_moto < 0:
            raise ValueError(
                "Las capacidades no pueden ser negativas."
            )

        return self.repositorio.actualizar_capacidades(
            sede_id=sede_id,
            cupos_carro=cupos_carro,
            cupos_moto=cupos_moto,
        )
