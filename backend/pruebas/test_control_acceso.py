from secrets import token_hex
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.infraestructura.base_datos.conexion import obtener_sesion
from app.modulos.accesos.presentacion.esquemas_ingreso import RegistrarIngresoEsquema
from app.modulos.accesos.presentacion.ingreso_router import registrar_ingreso, router
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.infraestructura.tokens_jwt import TokensJWT
from app.modulos.autenticacion.presentacion.dependencias_auth import (
    obtener_repositorio_usuario,
    obtener_tokens_jwt,
)
from app.modulos.carriles.dominio.carril import TipoCarril


@pytest.mark.parametrize("problema", ["direccion", "inactivo", "otra_sede", "inexistente"])
def test_rechaza_carril_incompatible_antes_de_registrar_ingreso(problema):
    sede_id = uuid4()
    carril_id = uuid4()
    datos = RegistrarIngresoEsquema(sede_id=sede_id, carril_id=carril_id, placa="ABC123")
    sesion = MagicMock()
    sesion.get.return_value = None
    if problema != "inexistente":
        sesion.get.return_value = SimpleNamespace(
            sede_id=uuid4() if problema == "otra_sede" else sede_id,
            activo=problema != "inactivo",
            tipo=TipoCarril.SALIDA if problema == "direccion" else TipoCarril.MIXTO,
        )

    with pytest.raises(HTTPException) as error:
        registrar_ingreso(datos, sesion, MagicMock())

    assert error.value.status_code == 422
    sesion.commit.assert_not_called()


@pytest.fixture
def ingreso_http(monkeypatch):
    sede_id, carril_id = uuid4(), uuid4()
    sesion = MagicMock()
    sesion.get.return_value = SimpleNamespace(sede_id=sede_id, activo=True, tipo=TipoCarril.MIXTO)
    usuarios = MagicMock()
    tokens = TokensJWT(token_hex(32), "HS256")
    ingreso = MagicMock()
    ingreso.return_value.ejecutar.return_value = SimpleNamespace(
        autorizado=True,
        decision_barrera="ABRIR",
        mensaje="Ingreso autorizado.",
        placa="ABC123",
        tipo_vehiculo="CARRO",
        es_reingreso=False,
        cupos_disponibles_restantes=1,
        acceso_id=uuid4(),
    )
    monkeypatch.setattr(
        "app.modulos.accesos.presentacion.ingreso_router.RegistrarIngresoVehiculo",
        ingreso,
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[obtener_sesion] = lambda: sesion
    app.dependency_overrides[obtener_repositorio_usuario] = lambda: usuarios
    app.dependency_overrides[obtener_tokens_jwt] = lambda: tokens
    with TestClient(app) as cliente:
        yield SimpleNamespace(
            cliente=cliente,
            tokens=tokens,
            usuarios=usuarios,
            ingreso=ingreso,
            sede_id=sede_id,
            carril_id=carril_id,
            datos={"sede_id": str(sede_id), "carril_id": str(carril_id), "placa": "ABC123"},
        )


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer token-invalido"}])
def test_ingreso_http_rechaza_solicitud_sin_token_valido(ingreso_http, headers):
    respuesta = ingreso_http.cliente.post(
        "/api/v1/accesos/ingreso", json=ingreso_http.datos, headers=headers
    )

    assert respuesta.status_code == 401
    ingreso_http.ingreso.assert_not_called()


@pytest.mark.parametrize("rol", [RolUsuario.OPERADOR, RolUsuario.ADMINISTRADOR])
def test_ingreso_http_permite_roles_autorizados(ingreso_http, rol):
    usuario = Usuario(
        username="usuario-prueba",
        password_hash="irrelevante-para-esta-prueba",
        nombre_completo="Usuario de prueba",
        rol=rol,
    )
    ingreso_http.usuarios.buscar_por_username.return_value = usuario
    token = ingreso_http.tokens.emitir(usuario)
    respuesta = ingreso_http.cliente.post(
        "/api/v1/accesos/ingreso",
        json=ingreso_http.datos,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["decision_barrera"] == "ABRIR"
    ingreso_http.ingreso.return_value.ejecutar.assert_called_once_with(
        sede_id=ingreso_http.sede_id, carril_id=ingreso_http.carril_id, placa_raw="ABC123"
    )
