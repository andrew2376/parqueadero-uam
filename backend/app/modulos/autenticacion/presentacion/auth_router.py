from fastapi import APIRouter, Depends, HTTPException, status

from app.modulos.autenticacion.aplicacion.servicio_autenticacion import (
    AutenticarUsuario,
)
from app.modulos.autenticacion.dominio.usuario import Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio
from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import PasswordHasherArgon2
from app.modulos.autenticacion.infraestructura.tokens_jwt import TokensJWT
from app.modulos.autenticacion.presentacion.dependencias_auth import (
    obtener_repositorio_usuario,
    obtener_tokens_jwt,
    obtener_usuario_actual,
)
from app.modulos.autenticacion.presentacion.esquemas_auth import (
    LoginEsquema,
    RespuestaLoginEsquema,
    UsuarioSesionEsquema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación y Sesión"],
)
_password_hasher = PasswordHasherArgon2()


@router.post(
    "/login",
    response_model=RespuestaLoginEsquema,
    status_code=status.HTTP_200_OK,
    summary="Inicio de sesión institucional UAM (S115 / S207)",
)
def login(
    datos: LoginEsquema,
    repositorio: UsuarioRepositorio = Depends(obtener_repositorio_usuario),
    tokens: TokensJWT = Depends(obtener_tokens_jwt),
) -> RespuestaLoginEsquema:
    caso_uso = AutenticarUsuario(
        repositorio=repositorio, password_hasher=_password_hasher, emitir_token=tokens.emitir
    )
    try:
        token, usuario = caso_uso.ejecutar(
            username=datos.username,
            password_plano=datos.password,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

    return RespuestaLoginEsquema(
        token=token,
        tipoToken="Bearer",
        usuario=UsuarioSesionEsquema(
            id=usuario.id,
            username=usuario.username,
            nombreCompleto=usuario.nombre_completo,
            rol=usuario.rol,
        ),
    )


@router.get(
    "/perfil",
    response_model=UsuarioSesionEsquema,
    status_code=status.HTTP_200_OK,
    summary="Consultar datos del usuario autenticado",
)
def obtener_perfil(
    usuario: Usuario = Depends(obtener_usuario_actual),
) -> UsuarioSesionEsquema:
    return UsuarioSesionEsquema(
        id=usuario.id,
        username=usuario.username,
        nombreCompleto=usuario.nombre_completo,
        rol=usuario.rol,
    )
