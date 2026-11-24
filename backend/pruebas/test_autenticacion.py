from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID

import jwt
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.configuracion import Configuracion, obtener_configuracion
from app.modulos.autenticacion.aplicacion.servicio_autenticacion import AutenticarUsuario
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import PasswordHasherArgon2
from app.modulos.autenticacion.infraestructura.tokens_jwt import TokensJWT
from app.modulos.autenticacion.infraestructura.usuario_repositorio_memoria import (
    UsuarioRepositorioMemoria,
)
from app.modulos.autenticacion.presentacion.auth_router import router
from app.modulos.autenticacion.presentacion.dependencias_auth import (
    obtener_tokens_jwt,
    requerir_rol,
)


@pytest.fixture
def password_hasher():
    return PasswordHasherArgon2()


@pytest.fixture
def repositorio(password_hasher):
    return UsuarioRepositorioMemoria(password_hasher)


@pytest.fixture
def clave_prueba():
    return token_urlsafe(64)


@pytest.fixture
def tokens(clave_prueba):
    return TokensJWT(clave_prueba, "HS256")


@pytest.fixture
def autenticador(repositorio, password_hasher, tokens):
    return AutenticarUsuario(repositorio, password_hasher, tokens.emitir)


def test_hasheo_y_verificacion_password(password_hasher):
    password = "clave_secreta_123"
    password_hash = password_hasher.hashear(password)

    assert password_hash.startswith("$argon2id$")
    assert password_hash != password_hasher.hashear(password)
    assert password_hasher.verificar(password, password_hash) is True
    assert password_hasher.verificar("otra_clave", password_hash) is False
    assert password_hasher.verificar(password, "$argon2id$invalido") is False
    assert password_hasher.verificar(password, "hash-no-argon2") is False


def test_autenticar_operador_exitoso(autenticador, tokens):
    token, usuario = autenticador.ejecutar(username=" Operador1 ", password_plano="operador123")

    assert usuario.id == UUID("00000000-0000-0000-0000-000000000001")
    assert usuario.username == "operador1"
    assert usuario.rol == RolUsuario.OPERADOR
    assert token is not None

    payload = tokens.decodificar(token)
    assert payload["username"] == "operador1"
    assert payload["rol"] == "OPERADOR"


def test_autenticar_admin_exitoso(autenticador):
    _, usuario = autenticador.ejecutar(username="admin", password_plano="admin123")

    assert usuario.id == UUID("00000000-0000-0000-0000-000000000002")
    assert usuario.username == "admin"
    assert usuario.rol == RolUsuario.ADMINISTRADOR


def test_autenticacion_falla_con_password_incorrecto(autenticador):
    with pytest.raises(ValueError, match="Credenciales inválidas"):
        autenticador.ejecutar(username="operador1", password_plano="clave_falsa")


def test_autenticacion_falla_con_usuario_inexistente(autenticador):
    with pytest.raises(ValueError, match="Credenciales inválidas"):
        autenticador.ejecutar(username="fantasma", password_plano="123456")


def test_autenticacion_falla_con_usuario_inactivo(autenticador, repositorio):
    usuario = repositorio.buscar_por_username("operador1")
    assert usuario is not None
    usuario.activo = False
    with pytest.raises(ValueError, match="Credenciales inválidas"):
        autenticador.ejecutar(username="operador1", password_plano="operador123")


def test_roles_jerarquia_administrador_tiene_todos_los_roles():
    usr_admin = Usuario(
        username="admin",
        password_hash="...",
        nombre_completo="Admin UAM",
        rol=RolUsuario.ADMINISTRADOR,
    )
    usr_operador = Usuario(
        username="operador1",
        password_hash="...",
        nombre_completo="Operador UAM",
        rol=RolUsuario.OPERADOR,
    )

    # Administrador tiene acceso a nivel operador y administrador
    assert usr_admin.tiene_rol(RolUsuario.OPERADOR) is True
    assert usr_admin.tiene_rol(RolUsuario.ADMINISTRADOR) is True

    # Operador solo tiene nivel operador
    assert usr_operador.tiene_rol(RolUsuario.OPERADOR) is True
    assert usr_operador.tiene_rol(RolUsuario.ADMINISTRADOR) is False


def test_requerir_rol_bloquea_operador_en_ruta_admin():
    usr_operador = Usuario(
        username="operador1",
        password_hash="...",
        nombre_completo="Operador UAM",
        rol=RolUsuario.OPERADOR,
    )

    filtro_admin = requerir_rol(RolUsuario.ADMINISTRADOR)

    with pytest.raises(HTTPException) as exc:
        filtro_admin(usuario=usr_operador)

    assert exc.value.status_code == 403


@pytest.fixture
def cliente_auth(tokens):
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[obtener_tokens_jwt] = lambda: tokens
    with TestClient(app) as cliente:
        yield cliente


@pytest.mark.parametrize(
    ("username", "password", "rol", "id_usuario", "nombre"),
    [
        (
            "operador1",
            "operador123",
            "OPERADOR",
            "00000000-0000-0000-0000-000000000001",
            "Operador de Turno UAM",
        ),
        (
            "admin",
            "admin123",
            "ADMINISTRADOR",
            "00000000-0000-0000-0000-000000000002",
            "Administrador de Parqueadero UAM",
        ),
    ],
)
def test_contrato_http_login_y_perfil(
    cliente_auth, tokens, username, password, rol, id_usuario, nombre
):
    login = cliente_auth.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert login.status_code == 200
    datos = login.json()
    usuario = {"id": id_usuario, "username": username, "nombreCompleto": nombre, "rol": rol}
    assert datos == {"token": datos["token"], "tipoToken": "Bearer", "usuario": usuario}
    assert tokens.decodificar(datos["token"])["sub"] == id_usuario

    perfil = cliente_auth.get(
        "/api/v1/auth/perfil", headers={"Authorization": f"Bearer {datos['token']}"}
    )
    assert perfil.status_code == 200
    assert perfil.json() == usuario


def test_http_rechaza_credenciales_y_tokens_invalidos(cliente_auth):
    login = cliente_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "mal"})
    perfil = cliente_auth.get("/api/v1/auth/perfil", headers={"Authorization": "Bearer invalido"})
    perfil_sin_token = cliente_auth.get("/api/v1/auth/perfil")

    for respuesta in (login, perfil, perfil_sin_token):
        assert respuesta.status_code == 401
        assert respuesta.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "caso", ["expirado", "otra_clave", "otro_algoritmo", "sin_exp", "otro_sub"]
)
def test_perfil_rechaza_jwt_fuera_del_contrato(cliente_auth, clave_prueba, caso):
    ahora = datetime.now(UTC)
    payload = {
        "sub": "00000000-0000-0000-0000-000000000002",
        "username": "admin",
        "exp": ahora + timedelta(minutes=1),
    }
    if caso == "expirado":
        payload["exp"] = ahora - timedelta(minutes=1)
    if caso == "sin_exp":
        del payload["exp"]
    if caso == "otro_sub":
        payload["sub"] = "00000000-0000-0000-0000-000000000001"

    clave = token_urlsafe(64) if caso == "otra_clave" else clave_prueba
    algoritmo = "HS384" if caso == "otro_algoritmo" else "HS256"
    token = jwt.encode(payload, clave, algorithm=algoritmo)

    perfil = cliente_auth.get("/api/v1/auth/perfil", headers={"Authorization": f"Bearer {token}"})
    assert perfil.status_code == 401
    assert perfil.headers["WWW-Authenticate"] == "Bearer"


def test_jwt_lee_clave_y_algoritmo_de_dotenv(monkeypatch, tmp_path, clave_prueba, repositorio):
    for nombre in ("URL_BASE_DATOS", "SECRETO_JWT", "ALGORITMO_JWT"):
        monkeypatch.delenv(nombre, raising=False)
    prueba_env = tmp_path / ".env"
    prueba_env.write_text(
        f"URL_BASE_DATOS=sqlite://\nSECRETO_JWT={clave_prueba}\nALGORITMO_JWT=HS384\n",
        encoding="utf-8",
    )
    monkeypatch.setitem(Configuracion.model_config, "env_file", prueba_env)
    obtener_configuracion.cache_clear()
    try:
        usuario = repositorio.buscar_por_username("admin")
        assert usuario is not None
        token = obtener_tokens_jwt().emitir(usuario)
        assert jwt.get_unverified_header(token)["alg"] == "HS384"
        assert jwt.decode(token, clave_prueba, algorithms=["HS384"])["sub"] == str(usuario.id)
    finally:
        obtener_configuracion.cache_clear()


def test_configuracion_exige_secreto_jwt(monkeypatch):
    monkeypatch.delenv("SECRETO_JWT", raising=False)
    with pytest.raises(ValidationError, match="secreto_jwt"):
        Configuracion(_env_file=None, url_base_datos="sqlite://")


def test_jwt_rechaza_clave_vacia_y_algoritmo_no_admitido(clave_prueba):
    with pytest.raises(ValueError, match="SECRETO_JWT"):
        TokensJWT(" ", "HS256")
    with pytest.raises(ValueError, match="ALGORITMO_JWT"):
        TokensJWT(clave_prueba, "none")
