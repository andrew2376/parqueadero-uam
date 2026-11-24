from uuid import uuid4

import pytest

from app.modulos.carriles.dominio.carril import (
    Carril,
    TipoCarril,
)
from app.modulos.carriles.dominio.carril_repositorio import (
    CarrilRepositorio,
)
from app.modulos.eventos_lectura.aplicacion.registrar_evento_lectura import (
    RegistrarEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EstadoEventoLectura,
    OrigenEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura_repositorio import (
    EventoLecturaRepositorio,
)
from app.modulos.reconocimiento_placas.aplicacion.registrar_evento_desde_lpr import (
    RegistrarEventoDesdeLPR,
)
from app.modulos.reconocimiento_placas.infraestructura.lector_lpr_simulado import (
    LectorLPRSimulado,
)
from datetime import datetime


class CarrilRepositorioFake(CarrilRepositorio):
    def __init__(self, carriles=None):
        self.carriles = carriles or {}

    def guardar(self, carril):
        self.carriles[carril.id] = carril
        return carril

    def obtener_por_id(self, carril_id):
        return self.carriles.get(carril_id)

    def listar_por_sede(self, sede_id):
        return [carril for carril in self.carriles.values() if carril.sede_id == sede_id]

    def actualizar(self, carril):
        self.carriles[carril.id] = carril
        return carril


class EventoLecturaRepositorioFake(EventoLecturaRepositorio):
    def __init__(self):
        self.eventos = {}

    def guardar(self, evento):
        self.eventos[evento.id] = evento
        return evento

    def obtener_por_id(self, evento_id):
        return self.eventos.get(evento_id)

    def listar_por_sede(self, sede_id):
        return [
            evento
            for evento in self.eventos.values()
            if evento.sede_id == sede_id
        ]

    def listar_filtrado(
        self,
        placa=None,
        sede_id=None,
        estado=None,
        origen=None,
        fecha_desde=None,
        fecha_hasta=None,
        pagina=1,
        limite=20,
    ):
        eventos = list(self.eventos.values())

        if placa:
            placa_normalizada = placa.strip().upper()
            eventos = [
                evento
                for evento in eventos
                if evento.placa == placa_normalizada
            ]

        if sede_id:
            eventos = [
                evento
                for evento in eventos
                if evento.sede_id == sede_id
            ]

        if estado:
            eventos = [
                evento
                for evento in eventos
                if evento.estado == estado
            ]

        if origen:
            eventos = [
                evento
                for evento in eventos
                if evento.origen == origen
            ]

        if fecha_desde:
            eventos = [
                evento
                for evento in eventos
                if evento.fecha_hora >= fecha_desde
            ]

        if fecha_hasta:
            eventos = [
                evento
                for evento in eventos
                if evento.fecha_hora <= fecha_hasta
            ]

        # Ordenar por fecha descendente
        eventos.sort(
            key=lambda evento: evento.fecha_hora,
            reverse=True,
        )

        # Total antes de aplicar paginación
        total = len(eventos)

        # Aplicar paginación
        desplazamiento = (pagina - 1) * limite
        eventos_paginados = eventos[desplazamiento:desplazamiento + limite]

        return eventos_paginados, total

@pytest.fixture
def entorno():
    sede_id = uuid4()

    carril = Carril(
        id=uuid4(),
        sede_id=sede_id,
        nombre="Carril de entrada",
        tipo=TipoCarril.ENTRADA,
    )

    carriles = CarrilRepositorioFake({carril.id: carril})

    eventos = EventoLecturaRepositorioFake()

    registrar_evento = RegistrarEventoLectura(
        eventos=eventos,
        carriles=carriles,
    )

    registrar_desde_lpr = RegistrarEventoDesdeLPR(
        carriles=carriles,
        registrar_evento=registrar_evento,
    )

    return {
        "carril": carril,
        "carriles": carriles,
        "eventos": eventos,
        "registrar": registrar_desde_lpr,
    }


def test_registrar_lectura_lpr_exitosa(entorno):
    carril = entorno["carril"]

    lector = LectorLPRSimulado(
        placa_fija="ABC123",
        confianza_fija=95.0,
    )

    lectura = lector.capturar_lectura(carril.id)

    evento = entorno["registrar"].ejecutar(lectura)

    assert evento.placa == "ABC123"
    assert evento.sede_id == carril.sede_id
    assert evento.carril_id == carril.id
    assert evento.confianza == 95.0
    assert evento.origen == OrigenEventoLectura.AUTOMATICO
    assert evento.estado == EstadoEventoLectura.EXITOSA

    assert len(entorno["eventos"].eventos) == 1


def test_registrar_lectura_con_baja_confianza(entorno):
    carril = entorno["carril"]

    lector = LectorLPRSimulado(
        placa_fija="ABC123",
        confianza_fija=60.0,
    )

    lectura = lector.capturar_lectura(carril.id)

    evento = entorno["registrar"].ejecutar(lectura)

    assert evento.placa == "ABC123"
    assert evento.confianza == 60.0
    assert evento.estado == EstadoEventoLectura.BAJA_CONFIANZA
    assert len(entorno["eventos"].eventos) == 1


def test_registrar_lectura_fallida(entorno):
    carril = entorno["carril"]

    lector = LectorLPRSimulado(
        placa_fija="",
        confianza_fija=0.0,
    )

    lectura = lector.capturar_lectura(carril.id)

    evento = entorno["registrar"].ejecutar(lectura)

    assert evento.placa is None
    assert evento.confianza == 0.0
    assert evento.estado == EstadoEventoLectura.FALLIDA
    assert evento.origen == OrigenEventoLectura.AUTOMATICO
    assert len(entorno["eventos"].eventos) == 1


def test_registrar_lectura_manual(entorno):
    carril = entorno["carril"]

    lector = LectorLPRSimulado()

    lectura = lector.simular_lectura_manual(
        carril_id=carril.id,
        placa="ABC123",
    )

    evento = entorno["registrar"].ejecutar(lectura)

    assert evento.placa == "ABC123"
    assert evento.origen == OrigenEventoLectura.MANUAL
    assert evento.estado == EstadoEventoLectura.EXITOSA
    assert len(entorno["eventos"].eventos) == 1


def test_no_registrar_lectura_si_el_carril_no_existe(entorno):
    lector = LectorLPRSimulado(
        placa_fija="ABC123",
        confianza_fija=95.0,
    )

    carril_inexistente = uuid4()
    lectura = lector.capturar_lectura(carril_inexistente)

    with pytest.raises(
        ValueError,
        match="El carril indicado no existe.",
    ):
        entorno["registrar"].ejecutar(lectura)

    assert len(entorno["eventos"].eventos) == 0
