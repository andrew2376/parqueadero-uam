
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modulos.eventos_lectura.aplicacion.registrar_evento_lectura import (
    RegistrarEventoLectura,
)
from app.modulos.eventos_lectura.dominio.evento_lectura import (
    EventoLectura,
    OrigenEventoLectura,
)


@pytest.fixture
def identificadores():
    return {
        "sede_id": uuid4(),
        "carril_id": uuid4(),
    }


@pytest.fixture
def evento(identificadores):
    return EventoLectura(
        sede_id=identificadores["sede_id"],
        carril_id=identificadores["carril_id"],
        placa="abc123",
        confianza=98.5,
        origen=OrigenEventoLectura.AUTOMATICO,
    )


@pytest.fixture
def repositorios():
    eventos = MagicMock()
    carriles = MagicMock()

    return eventos, carriles


def test_registrar_evento_correctamente(
    evento, repositorios
):
    eventos, carriles = repositorios

    carriles.obtener_por_id.return_value = SimpleNamespace(
        sede_id=evento.sede_id,
        activo=True,
    )
    eventos.guardar.return_value = evento

    caso_uso = RegistrarEventoLectura(eventos, carriles)

    resultado = caso_uso.ejecutar(evento)

    assert resultado == evento
    eventos.guardar.assert_called_once_with(evento)


def test_no_registrar_si_el_carril_no_existe(
    evento, repositorios
):
    eventos, carriles = repositorios

    carriles.obtener_por_id.return_value = None

    caso_uso = RegistrarEventoLectura(eventos, carriles)

    with pytest.raises(ValueError, match="El carril indicado no existe"):
        caso_uso.ejecutar(evento)

    eventos.guardar.assert_not_called()


def test_no_registrar_si_el_carril_pertenece_a_otra_sede(
    evento, repositorios
):
    eventos, carriles = repositorios

    carriles.obtener_por_id.return_value = SimpleNamespace(
        sede_id=uuid4(),
        activo=True,
    )

    caso_uso = RegistrarEventoLectura(eventos, carriles)

    with pytest.raises(
        ValueError,
        match="no pertenece a la sede especificada",
    ):
        caso_uso.ejecutar(evento)

    eventos.guardar.assert_not_called()
