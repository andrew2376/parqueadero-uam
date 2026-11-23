from uuid import UUID
from pydantic import BaseModel, Field

from app.modulos.autenticacion.dominio.usuario import RolUsuario


class LoginEsquema(BaseModel):
    username: str = Field(..., description="Nombre de usuario institucional")
    password: str = Field(..., description="Contraseña en texto plano")


class UsuarioSesionEsquema(BaseModel):
    id: UUID
    username: str
    nombreCompleto: str
    rol: RolUsuario


class RespuestaLoginEsquema(BaseModel):
    token: str
    tipoToken: str = "Bearer"
    usuario: UsuarioSesionEsquema
