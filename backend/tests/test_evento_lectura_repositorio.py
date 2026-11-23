
from datetime import time
from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infraestructura.base_datos.conexion import Base
from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo
from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EventoLectura,
    EstadoEventoLectura,
    OrigenEventoLectura,
)
from app.modulos.eventos_lectura.infraestructura.evento_lectura_repositorio_sqlalchemy import (
    EventoLecturaRepositorioSQLAlchemy,
)
from app.modulos.eventos_lectura.infraestructura.evento_lectura_modelo import (
    EventoLecturaModelo,
)
from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo


def crear_sesion_prueba():
    motor_prueba = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(motor_prueba, "connect")
    def activar_claves_foraneas(conexion, registro):
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(motor_prueba)

    return Session(motor_prueba), motor_prueba


def preparar_sede_y_carril(sesion: Session):
    sede = SedeModelo(
        id=uuid4(),
        nombre="Sede de pruebas",
        zona_horaria="America/Bogota",
        inicio_dia_operativo=time(5, 0),
        cupos_carro=100,
        cupos_moto=50,
    )

    sesion.add(sede)
    sesion.flush()

    carril = CarrilModelo(
        id=uuid4(),
        sede_id=sede.id,
        nombre="Entrada principal",
        tipo="ENTRADA",
        activo=True,
    )

    sesion.add(carril)
    sesion.commit()

    return sede, carril


def test_guardar_evento_lectura():
    sesion, motor = crear_sesion_prueba()

    try:
        sede, carril = preparar_sede_y_carril(sesion)

        evento = EventoLectura(
            sede_id=sede.id,
            carril_id=carril.id,
            placa="abc123",
            confianza=98.5,
            origen=OrigenEventoLectura.AUTOMATICO,
        )

        repositorio = EventoLecturaRepositorioSQLAlchemy(sesion)

        resultado = repositorio.guardar(evento)

        assert resultado.id == evento.id
        assert resultado.sede_id == sede.id
        assert resultado.carril_id == carril.id
        assert resultado.placa == "ABC123"
        assert resultado.confianza == 98.5
        assert resultado.origen == OrigenEventoLectura.AUTOMATICO
        assert resultado.estado == EstadoEventoLectura.EXITOSA

    finally:
        sesion.close()
        motor.dispose()


def test_obtener_evento_por_id():
    sesion, motor = crear_sesion_prueba()

    try:
        sede, carril = preparar_sede_y_carril(sesion)

        evento = EventoLectura(
            sede_id=sede.id,
            carril_id=carril.id,
            placa="xyz789",
            confianza=95.0,
            origen=OrigenEventoLectura.MANUAL,
        )

        repositorio = EventoLecturaRepositorioSQLAlchemy(sesion)
        guardado = repositorio.guardar(evento)

        resultado = repositorio.obtener_por_id(guardado.id)

        assert resultado is not None
        assert resultado.id == guardado.id
        assert resultado.placa == "XYZ789"
        assert resultado.origen == OrigenEventoLectura.MANUAL
        assert resultado.estado == EstadoEventoLectura.EXITOSA

    finally:
        sesion.close()
        motor.dispose()


def test_listar_eventos_por_sede():
    sesion, motor = crear_sesion_prueba()

    try:
        sede, carril = preparar_sede_y_carril(sesion)

        repositorio = EventoLecturaRepositorioSQLAlchemy(sesion)

        evento_1 = EventoLectura(
            sede_id=sede.id,
            carril_id=carril.id,
            placa="abc123",
            confianza=98.0,
            origen=OrigenEventoLectura.AUTOMATICO,
        )

        evento_2 = EventoLectura(
            sede_id=sede.id,
            carril_id=carril.id,
            placa="xyz789",
            confianza=96.0,
            origen=OrigenEventoLectura.MANUAL,
        )

        repositorio.guardar(evento_1)
        repositorio.guardar(evento_2)

        resultados = repositorio.listar_por_sede(sede.id)

        assert len(resultados) == 2
        assert {evento.placa for evento in resultados} == {
            "ABC123",
            "XYZ789",
        }

    finally:
        sesion.close()
        motor.dispose()


def test_guardar_evento_lectura_fallida():
    sesion, motor = crear_sesion_prueba()

    try:
        sede, carril = preparar_sede_y_carril(sesion)

        evento = EventoLectura(
            sede_id=sede.id,
            carril_id=carril.id,
            placa=None,
            confianza=0.0,
            origen=OrigenEventoLectura.AUTOMATICO,
            estado=EstadoEventoLectura.FALLIDA,
        )

        repositorio = EventoLecturaRepositorioSQLAlchemy(sesion)

        guardado = repositorio.guardar(evento)
        recuperado = repositorio.obtener_por_id(guardado.id)

        assert recuperado is not None
        assert recuperado.placa is None
        assert recuperado.estado == EstadoEventoLectura.FALLIDA
        assert recuperado.confianza == 0.0
        assert recuperado.origen == OrigenEventoLectura.AUTOMATICO

    finally:
        sesion.close()
        motor.dispose()
