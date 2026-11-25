from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("tipo", "direccion", "activo", "estado"),
    [
        ("ENTRADA", "ENTRADA", True, 201),
        ("ENTRADA", "SALIDA", True, 409),
        ("SALIDA", "ENTRADA", True, 409),
        ("SALIDA", "SALIDA", True, 201),
        ("MIXTO", "ENTRADA", True, 201),
        ("MIXTO", "SALIDA", True, 201),
        ("MIXTO", "SALIDA", False, 409),
        (None, "ENTRADA", False, 404),
    ],
)
def test_matriz_simulacion_lpr(monkeypatch, tipo, direccion, activo, estado):
    monkeypatch.setenv("URL_BASE_DATOS", "sqlite://")
    monkeypatch.setenv("SECRETO_JWT", "clave-solo-para-la-prueba")
    from app.modulos.autenticacion.presentacion.dependencias_auth import obtener_usuario_actual
    from app.modulos.reconocimiento_placas.presentacion import lpr_router as lpr

    sede_id, carril_id = uuid4(), uuid4()
    carril = SimpleNamespace(tipo=tipo, activo=activo)
    monkeypatch.setattr(
        lpr.CarrilRepositorioSQLAlchemy, "obtener_por_id", lambda *_: carril if tipo else None
    )
    guardados = []

    def registrar(lectura):
        guardados.append(lectura)
        return lpr.EventoLecturaRespuesta(
            id=uuid4(),
            sede_id=sede_id,
            carril_id=carril_id,
            placa=lectura.placa,
            confianza=lectura.confianza,
            origen="AUTOMATICO",
            estado=lectura.estado,
            fecha_hora=lectura.creado_en,
        )

    monkeypatch.setattr(
        lpr, "construir_registrador_eventos", lambda _: SimpleNamespace(ejecutar=registrar)
    )
    app = FastAPI()
    app.include_router(lpr.router)
    app.dependency_overrides[lpr.obtener_sesion] = lambda: None
    app.dependency_overrides[obtener_usuario_actual] = lambda: SimpleNamespace(
        tiene_rol=lambda rol: rol == lpr.RolUsuario.OPERADOR
    )

    with TestClient(app) as cliente:
        respuesta = cliente.post(
            "/lecturas-lpr/simulacion", params={"carril_id": str(carril_id), "direccion": direccion}
        )
    assert respuesta.status_code == estado, respuesta.text
    if estado == 201:
        assert respuesta.json()["direccion"] == direccion
        assert len(guardados) == 1
    else:
        assert not guardados
