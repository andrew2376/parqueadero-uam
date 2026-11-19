
from uuid import UUID, uuid4

from app.modulos.carriles.dominio.carril import Carril, TipoCarril
from app.modulos.carriles.dominio.carril_repositorio import CarrilRepositorio


class CrearCarril:

    def __init__(self, repositorio: CarrilRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        sede_id: UUID,
        nombre: str,
        tipo: TipoCarril,
    ) -> Carril:
        carril = Carril(
            id=uuid4(),
            sede_id=sede_id,
            nombre=nombre,
            tipo=tipo,
        )

        return self.repositorio.guardar(carril)


class ObtenerCarril:

    def __init__(self, repositorio: CarrilRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, carril_id: UUID) -> Carril | None:
        return self.repositorio.obtener_por_id(carril_id)


class ListarCarrilesPorSede:

    def __init__(self, repositorio: CarrilRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, sede_id: UUID) -> list[Carril]:
        return self.repositorio.listar_por_sede(sede_id)


class ActualizarCarril:

    def __init__(self, repositorio: CarrilRepositorio):
        self.repositorio = repositorio

    def ejecutar(
        self,
        carril_id: UUID,
        nombre: str,
        tipo: TipoCarril,
    ) -> Carril:
        carril = self.repositorio.obtener_por_id(carril_id)

        if carril is None:
            raise ValueError("El carril no existe.")

        carril.nombre = nombre
        carril.tipo = tipo

        return self.repositorio.actualizar(carril)


class CambiarEstadoCarril:

    def __init__(self, repositorio: CarrilRepositorio):
        self.repositorio = repositorio

    def ejecutar(self, carril_id: UUID, activo: bool) -> Carril:
        carril = self.repositorio.obtener_por_id(carril_id)

        if carril is None:
            raise ValueError("El carril no existe.")

        if activo:
            carril.activar()
        else:
            carril.desactivar()

        return self.repositorio.actualizar(carril)
