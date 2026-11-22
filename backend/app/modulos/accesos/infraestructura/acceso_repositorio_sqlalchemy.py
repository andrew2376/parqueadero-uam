from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modulos.accesos.dominio.acceso_repositorio import AccesoRepositorio
from app.modulos.accesos.dominio.ingreso import EstadoAcceso, RegistroIngreso
from app.modulos.accesos.infraestructura.acceso_modelo import AccesoModelo
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class AccesoRepositorioSQLAlchemy(AccesoRepositorio):

    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar_ingreso(self, ingreso: RegistroIngreso) -> RegistroIngreso:
        modelo = self.sesion.get(AccesoModelo, ingreso.id)
        if modelo is None:
            modelo = AccesoModelo(
                id=ingreso.id,
                sede_id=ingreso.sede_id,
                carril_id=ingreso.carril_id,
                placa=ingreso.placa,
                tipo_vehiculo=ingreso.tipo_vehiculo,
                fecha_ingreso=ingreso.fecha_ingreso,
                fecha_salida=ingreso.fecha_salida,
                estado=ingreso.estado,
                es_reingreso=ingreso.es_reingreso,
            )
            self.sesion.add(modelo)
        else:
            modelo.fecha_salida = ingreso.fecha_salida
            modelo.estado = ingreso.estado
            modelo.es_reingreso = ingreso.es_reingreso

        self.sesion.commit()
        return ingreso

    def buscar_ingreso_activo_por_placa(self, placa: str, sede_id: UUID) -> RegistroIngreso | None:
        modelo = (
            self.sesion.query(AccesoModelo)
            .filter(
                AccesoModelo.placa == placa,
                AccesoModelo.sede_id == sede_id,
                AccesoModelo.estado == EstadoAcceso.ACTIVO,
            )
            .first()
        )
        if modelo is None:
            return None

        return RegistroIngreso(
            id=modelo.id,
            sede_id=modelo.sede_id,
            carril_id=modelo.carril_id,
            placa=modelo.placa,
            tipo_vehiculo=modelo.tipo_vehiculo,
            fecha_ingreso=modelo.fecha_ingreso,
            fecha_salida=modelo.fecha_salida,
            estado=modelo.estado,
            es_reingreso=modelo.es_reingreso,
        )

    def contar_vehiculos_activos(self, sede_id: UUID, tipo_vehiculo: TipoVehiculo) -> int:
        conteo = (
            self.sesion.query(func.count(AccesoModelo.id))
            .filter(
                AccesoModelo.sede_id == sede_id,
                AccesoModelo.tipo_vehiculo == tipo_vehiculo,
                AccesoModelo.estado == EstadoAcceso.ACTIVO,
            )
            .scalar()
        )
        return conteo or 0
