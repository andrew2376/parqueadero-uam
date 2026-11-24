from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.configuracion import obtener_configuracion
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import (
    RepositorioUsuariosNoDisponible,
    UsuarioRepositorio,
)
from app.modulos.autenticacion.infraestructura.tokens_jwt import TokensJWT

esquema_seguridad_bearer = HTTPBearer(auto_error=False)


def obtener_repositorio_usuario() -> UsuarioRepositorio:
    raise RuntimeError("Configura un proveedor de UsuarioRepositorio para esta aplicación.")


def responder_repositorio_no_disponible(
    _request: Request, _error: RepositorioUsuariosNoDisponible
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "El servicio de autenticación no está disponible temporalmente."},
    )


def obtener_tokens_jwt() -> TokensJWT:
    configuracion = obtener_configuracion()
    return TokensJWT(configuracion.secreto_jwt, configuracion.algoritmo_jwt)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_seguridad_bearer),
    repositorio: UsuarioRepositorio = Depends(obtener_repositorio_usuario),
    tokens: TokensJWT = Depends(obtener_tokens_jwt),
) -> Usuario:
    """Extrae y valida el token Bearer para identificar al usuario."""
    if not credenciales:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no proporcionado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = tokens.decodificar(credenciales.credentials)
        username = payload["username"]
        if not isinstance(username, str):
            raise jwt.InvalidTokenError("El nombre de usuario del token no es válido.")
    except jwt.PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    usuario = repositorio.buscar_por_username(username)
    if not usuario or not usuario.activo or str(usuario.id) != payload["sub"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


def requerir_rol(rol_esperado: RolUsuario) -> Callable:
    """Valida que el usuario autenticado cuente con los permisos necesarios."""

    def dependencia_rol(
        usuario: Usuario = Depends(obtener_usuario_actual),
    ) -> Usuario:
        if not usuario.tiene_rol(rol_esperado):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: se requiere rol {rol_esperado.value}.",
            )
        return usuario

    return dependencia_rol
