import pytest
from fastapi import HTTPException

from app.modulos.autenticacion.aplicacion.servicio_autenticacion import (
    AutenticarUsuario,
    decodificar_token,
    hashear_password,
    verificar_password,
)
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.infraestructura.usuario_repositorio_memoria import (
    UsuarioRepositorioMemoria,
)
from app.modulos.autenticacion.presentacion.auth_router import login
from app.modulos.autenticacion.presentacion.dependencias_auth import requerir_rol
from app.modulos.autenticacion.presentacion.esquemas_auth import LoginEsquema


def test_hasheo_y_verificacion_password():
    password = "clave_secreta_123"
    password_hash = hashear_password(password)

    assert password_hash != password
    assert verificar_password(password, password_hash) is True
    assert verificar_password("otra_clave", password_hash) is False


def test_autenticar_operador_exitoso():
    repo = UsuarioRepositorioMemoria()
    caso_uso = AutenticarUsuario(repositorio=repo)

    token, usuario = caso_uso.ejecutar(username="operador1", password_plano="operador123")

    assert usuario.username == "operador1"
    assert usuario.rol == RolUsuario.OPERADOR
    assert token is not None

    payload = decodificar_token(token)
    assert payload["username"] == "operador1"
    assert payload["rol"] == "OPERADOR"


def test_autenticar_admin_exitoso():
    repo = UsuarioRepositorioMemoria()
    caso_uso = AutenticarUsuario(repositorio=repo)

    token, usuario = caso_uso.ejecutar(username="admin", password_plano="admin123")

    assert usuario.username == "admin"
    assert usuario.rol == RolUsuario.ADMINISTRADOR


def test_autenticacion_falla_con_password_incorrecto():
    repo = UsuarioRepositorioMemoria()
    caso_uso = AutenticarUsuario(repositorio=repo)

    with pytest.raises(ValueError, match="Credenciales inválidas"):
        caso_uso.ejecutar(username="operador1", password_plano="clave_falsa")


def test_autenticacion_falla_con_usuario_inexistente():
    repo = UsuarioRepositorioMemoria()
    caso_uso = AutenticarUsuario(repositorio=repo)

    with pytest.raises(ValueError, match="Credenciales inválidas"):
        caso_uso.ejecutar(username="fantasma", password_plano="123456")


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


def test_login_router_endpoint():
    repo = UsuarioRepositorioMemoria()
    solicitud = LoginEsquema(username="operador1", password="operador123")

    res = login(datos=solicitud, repositorio=repo)

    assert res.token is not None
    assert res.usuario.username == "operador1"
    assert res.usuario.rol == RolUsuario.OPERADOR
    assert res.tipoToken == "Bearer"
