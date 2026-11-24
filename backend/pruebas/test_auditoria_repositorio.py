from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infraestructura.base_datos.conexion import Base
from app.modulos.auditoria.dominio.auditoria import Auditoria
from app.modulos.auditoria.infraestructura.auditoria_modelo import AuditoriaModelo
from app.modulos.auditoria.infraestructura.auditoria_repositorio_sqlalchemy import (
    AuditoriaRepositorioSQLAlchemy,
)


def crear_sesion_prueba():
    motor_prueba = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(motor_prueba)

    return Session(motor_prueba), motor_prueba


def crear_auditoria(
    accion: str = "CREAR",
    entidad: str = "Producto",
    entidad_id: str = "123",
    usuario_id=None,
    username: str = "admin",
    fecha_hora: datetime | None = None,
):
    return Auditoria(
        usuario_id=usuario_id,
        username=username,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        fecha_hora=fecha_hora or datetime.now(UTC),
        detalles={"origen": "prueba"},
    )


def test_registrar_auditoria():
    sesion, motor = crear_sesion_prueba()

    try:
        usuario_id = uuid4()
        auditoria = crear_auditoria(usuario_id=usuario_id)

        repositorio = AuditoriaRepositorioSQLAlchemy(sesion)

        resultado = repositorio.registrar(auditoria)

        assert resultado.id is not None
        assert resultado.usuario_id == usuario_id
        assert resultado.username == "admin"
        assert resultado.accion == "CREAR"
        assert resultado.entidad == "Producto"
        assert resultado.entidad_id == "123"
        assert resultado.detalles == {"origen": "prueba"}

        registro_bd = sesion.query(AuditoriaModelo).filter_by(id=resultado.id).first()

        assert registro_bd is not None

    finally:
        sesion.close()
        motor.dispose()


def test_consultar_auditorias_por_filtros():
    sesion, motor = crear_sesion_prueba()

    try:
        usuario_id = uuid4()
        fecha_base = datetime.now(UTC)

        repositorio = AuditoriaRepositorioSQLAlchemy(sesion)

        auditoria_1 = crear_auditoria(
            accion="CREAR",
            entidad="Producto",
            entidad_id="1",
            usuario_id=usuario_id,
            fecha_hora=fecha_base,
        )

        auditoria_2 = crear_auditoria(
            accion="ELIMINAR",
            entidad="Producto",
            entidad_id="2",
            usuario_id=usuario_id,
            fecha_hora=fecha_base + timedelta(minutes=5),
        )

        auditoria_3 = crear_auditoria(
            accion="ACTUALIZAR",
            entidad="Tarifa",
            entidad_id="3",
            usuario_id=uuid4(),
            fecha_hora=fecha_base + timedelta(minutes=10),
        )

        repositorio.registrar(auditoria_1)
        repositorio.registrar(auditoria_2)
        repositorio.registrar(auditoria_3)

        resultados = repositorio.consultar(
            usuario_id=usuario_id,
            entidad="Producto",
        )

        assert len(resultados) == 2
        assert {resultado.accion for resultado in resultados} == {
            "CREAR",
            "ELIMINAR",
        }

    finally:
        sesion.close()
        motor.dispose()


def test_consultar_auditorias_por_fecha_y_limite():
    sesion, motor = crear_sesion_prueba()

    try:
        fecha_base = datetime.now(UTC)

        repositorio = AuditoriaRepositorioSQLAlchemy(sesion)

        for numero in range(5):
            auditoria = crear_auditoria(
                accion="ACTUALIZAR",
                entidad="Carril",
                entidad_id=str(numero),
                fecha_hora=fecha_base + timedelta(minutes=numero),
            )

            repositorio.registrar(auditoria)

        resultados = repositorio.consultar(
            desde=fecha_base + timedelta(minutes=2),
            limite=2,
        )

        assert len(resultados) == 2
        assert resultados[0].fecha_hora >= resultados[1].fecha_hora

    finally:
        sesion.close()
        motor.dispose()
        