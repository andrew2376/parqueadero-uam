from collections.abc import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.modulos.autenticacion.aplicacion.servicio_autenticacion import (
    decodificar_token,
)
from app.modulos.autenticacion.dominio.usuario import RolUsuario, Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio
from app.modulos.autenticacion.infraestructura.usuario_repositorio_memoria import (
    obtener_repositorio_usuario,
)

esquema_seguridad_bearer = HTTPBearer(auto_error=False)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_seguridad_bearer),
    repositorio: UsuarioRepositorio = Depends(obtener_repositorio_usuario),
) -> Usuario:
    """Extrae y valida el token Bearer para identificar al usuario."""
    if not credenciales:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación no proporcionado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decodificar_token(credenciales.credentials)
        username: str = payload.get("username", "")
    except jwt.PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    usuario = repositorio.buscar_por_username(username)
    if not usuario or not usuario.activo:
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
