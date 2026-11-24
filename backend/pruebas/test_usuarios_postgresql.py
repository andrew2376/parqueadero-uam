from os import getenv
from secrets import token_urlsafe
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import PasswordHasherArgon2
from app.modulos.autenticacion.infraestructura.usuarios_demo import USUARIOS_DEMO

BASE_PRUEBA = "parqueadero_s115_test"


@pytest.fixture
def conexion_postgresql(monkeypatch):
    url_configurada = getenv("S115_POSTGRES_TEST_URL")
    if not url_configurada:
        pytest.skip("Configura S115_POSTGRES_TEST_URL para la base descartable de S115.")

    url = make_url(url_configurada)
    if url.get_backend_name() != "postgresql" or url.database != BASE_PRUEBA:
        pytest.fail(f"S115_POSTGRES_TEST_URL debe apuntar al PostgreSQL {BASE_PRUEBA}.")
    monkeypatch.setenv("URL_BASE_DATOS", url_configurada)
    monkeypatch.setenv("SECRETO_JWT", token_urlsafe(64))
    monkeypatch.setenv("ALGORITMO_JWT", "HS256")

    motor = create_engine(url, hide_parameters=True)
    try:
        with motor.connect() as conexion:
            transaccion = conexion.begin()
            try:
                assert conexion.scalar(select(func.current_database())) == BASE_PRUEBA
                assert "7b11651f5a01" in MigrationContext.configure(conexion).get_current_heads()
                yield conexion
            finally:
                transaccion.rollback()
    finally:
        motor.dispose()


def test_carga_idempotente_y_login_con_repositorio_postgresql(conexion_postgresql, monkeypatch):
    from app.infraestructura.base_datos.conexion import obtener_sesion
    from app.main import aplicacion
    from app.modulos.autenticacion.infraestructura.cargar_usuarios_demo import cargar_usuarios_demo
    from app.modulos.autenticacion.infraestructura.usuario_modelo import UsuarioModelo
    from app.modulos.autenticacion.infraestructura.usuario_repositorio_sqlalchemy import (
        UsuarioRepositorioSQLAlchemy,
    )

    passwords = {demo.username: token_urlsafe(24) for demo in USUARIOS_DEMO}
    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        assert sesion.scalar(select(func.count()).select_from(UsuarioModelo)) == 0
        assert cargar_usuarios_demo(sesion, passwords) == 2
        sesion.commit()

    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        distintos = {demo.username: token_urlsafe(24) for demo in USUARIOS_DEMO}
        assert cargar_usuarios_demo(sesion, distintos) == 0
        repositorio = UsuarioRepositorioSQLAlchemy(sesion)
        hasher = PasswordHasherArgon2()
        for demo in USUARIOS_DEMO:
            usuario = repositorio.buscar_por_username(f" {demo.username.upper()} ")
            assert usuario is not None
            assert (usuario.id, usuario.nombre_completo, usuario.rol) == (
                demo.id,
                demo.nombre_completo,
                demo.rol,
            )
            assert usuario.password_hash.startswith("$argon2id$")
            assert hasher.verificar(passwords[demo.username], usuario.password_hash)
        sesion.commit()

    def sesion_prueba():
        with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
            yield sesion

    monkeypatch.setitem(aplicacion.dependency_overrides, obtener_sesion, sesion_prueba)
    with TestClient(aplicacion) as cliente:
        for demo in USUARIOS_DEMO:
            login = cliente.post(
                "/api/v1/auth/login",
                json={"username": demo.username, "password": passwords[demo.username]},
            )
            assert login.status_code == 200
            data = login.json()
            assert data["usuario"]["id"] == str(demo.id)
            perfil = cliente.get(
                "/api/v1/auth/perfil", headers={"Authorization": f"Bearer {data['token']}"}
            )
            assert perfil.status_code == 200
            assert perfil.json() == data["usuario"]


@pytest.mark.parametrize(("campo", "valor"), [("rol", "INVITADO"), ("username", " Admin ")])
def test_postgresql_aplica_las_restricciones_del_modelo(conexion_postgresql, campo, valor):
    from app.modulos.autenticacion.infraestructura.usuario_modelo import UsuarioModelo

    campos = {
        "id": uuid4(),
        "username": "usuario_prueba",
        "rol": "OPERADOR",
        "nombre_completo": "Usuario de prueba",
        "password_hash": PasswordHasherArgon2().hashear(token_urlsafe(24)),
    }
    campos[campo] = valor
    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        with pytest.raises(IntegrityError):
            with sesion.begin():
                sesion.add(UsuarioModelo(**campos))
