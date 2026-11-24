import hashlib
import hmac
from datetime import UTC, datetime, timedelta

import jwt

from app.modulos.autenticacion.dominio.usuario import Usuario
from app.modulos.autenticacion.dominio.usuario_repositorio import UsuarioRepositorio

# Clave secreta estándar para tokens JWT (mínimo 32 bytes para HMAC-SHA256)
CLAVE_SECRETA_JWT = "uam_parqueadero_secreto_super_seguro_jwt_2026_antonia_s207"
ALGORITMO_JWT = "HS256"
EXPIRACION_MINUTOS = 60 * 12  # 12 horas de sesión


def hashear_password(password: str) -> str:
    """Genera un hash seguro SHA-256 para almacenamiento de credenciales."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica si la contraseña ingresada coincide con el hash almacenado."""
    return hmac.compare_digest(hashear_password(password_plano), password_hash)


def generar_token(usuario: Usuario) -> str:
    """Emite un token JWT firmado con los datos del usuario y rol."""
    expiracion = datetime.now(UTC) + timedelta(minutes=EXPIRACION_MINUTOS)
    payload = {
        "sub": str(usuario.id),
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol.value,
        "exp": expiracion,
    }
    return jwt.encode(payload, CLAVE_SECRETA_JWT, algorithm=ALGORITMO_JWT)


def decodificar_token(token: str) -> dict:
    """Valida y decodifica el token JWT."""
    return jwt.decode(token, CLAVE_SECRETA_JWT, algorithms=[ALGORITMO_JWT])


class AutenticarUsuario:
    """Caso de uso para inicio de sesión."""

    def __init__(self, repositorio: UsuarioRepositorio) -> None:
        self.repositorio = repositorio

    def ejecutar(self, username: str, password_plano: str) -> tuple[str, Usuario]:
        usuario = self.repositorio.buscar_por_username(username.strip().lower())
        if not usuario or not usuario.activo:
            raise ValueError("Credenciales inválidas o usuario inactivo.")

        if not verificar_password(password_plano, usuario.password_hash):
            raise ValueError("Credenciales inválidas o usuario inactivo.")

        token = generar_token(usuario)
        return token, usuario
