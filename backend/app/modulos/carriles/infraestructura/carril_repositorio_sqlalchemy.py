from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.carriles.dominio.carril import Carril, TipoCarril
from app.modulos.carriles.dominio.carril_repositorio import CarrilRepositorio
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo


class CarrilRepositorioSQLAlchemy(CarrilRepositorio):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, carril: Carril) -> Carril:
        modelo = CarrilModelo(
            id=carril.id,
            sede_id=carril.sede_id,
            nombre=carril.nombre,
            tipo=carril.tipo.value,
            activo=carril.activo,
        )

        self.sesion.add(modelo)
        self.sesion.commit()
        self.sesion.refresh(modelo)

        return self._convertir_a_dominio(modelo)

    def obtener_por_id(self, carril_id: UUID) -> Carril | None:
        modelo = self.sesion.get(CarrilModelo, carril_id)

        if modelo is None:
            return None

        return self._convertir_a_dominio(modelo)

    def listar_por_sede(self, sede_id: UUID) -> list[Carril]:
        consulta = (
            select(CarrilModelo)
            .where(CarrilModelo.sede_id == sede_id)
            .order_by(CarrilModelo.nombre)
        )

        modelos = self.sesion.scalars(consulta).all()

        return [self._convertir_a_dominio(modelo) for modelo in modelos]

    def actualizar(self, carril: Carril) -> Carril:
        modelo = self.sesion.get(CarrilModelo, carril.id)

        if modelo is None:
            raise ValueError("El carril no existe.")

            modelo.nombre = carril.nombre
            modelo.tipo = carril.tipo.value
            modelo.activo = carril.activo

            self.sesion.flush()
            self.sesion.refresh(modelo)

            return self._convertir_a_dominio(modelo)

    @staticmethod
    def _convertir_a_dominio(modelo: CarrilModelo) -> Carril:
        return Carril(
            id=modelo.id,
            sede_id=modelo.sede_id,
            nombre=modelo.nombre,
            tipo=TipoCarril(modelo.tipo),
            activo=modelo.activo,
        )
