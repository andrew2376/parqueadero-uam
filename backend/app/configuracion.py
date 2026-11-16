
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Ruta del archivo .env ubicado en la raíz del proyecto
RUTA_ENV = Path(__file__).resolve().parents[2] / ".env"


class Configuracion(BaseSettings):
    nombre_aplicacion: str = "API Parqueadero LPR"
    entorno: str = "desarrollo"
    prefijo_api: str = "/api/v1"
    url_base_datos: str
    secreto_jwt: str
    algoritmo_jwt: str = "HS256"
    umbral_confianza_lectura: float = 0.85
    zona_horaria: str = "America/Bogota"
    origenes_permitidos: list[str] = ["http://localhost:4200"]

    model_config = SettingsConfigDict(
        env_file=RUTA_ENV,
        extra="ignore"
    )


@lru_cache
def obtener_configuracion() -> Configuracion:
    return Configuracion()
