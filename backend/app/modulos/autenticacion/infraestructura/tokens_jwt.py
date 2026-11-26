from datetime import UTC, datetime, timedelta

import jwt

from app.modulos.autenticacion.dominio.usuario import Usuario


class TokensJWT:
    def __init__(self, secreto: str, algoritmo: str) -> None:
        if not secreto.strip():
            raise ValueError("SECRETO_JWT debe contener una clave de firma.")
        if algoritmo not in {"HS256", "HS384", "HS512"}:
            raise ValueError("ALGORITMO_JWT debe ser HS256, HS384 o HS512.")

        self._secreto = secreto
        self._algoritmo = algoritmo

    def emitir(self, usuario: Usuario) -> str:
        payload = {
            "sub": str(usuario.id),
            "username": usuario.username,
            "nombre_completo": usuario.nombre_completo,
            "rol": usuario.rol.value,
            "exp": datetime.now(UTC) + timedelta(hours=12),
        }
        return jwt.encode(payload, self._secreto, algorithm=self._algoritmo)

    def decodificar(self, token: str) -> dict:
        return jwt.decode(
            token,
            self._secreto,
            algorithms=[self._algoritmo],
            options={"require": ["sub", "username", "exp"]},
        )
