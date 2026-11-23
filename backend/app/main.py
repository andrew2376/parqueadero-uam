from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuracion import obtener_configuracion
from app.infraestructura.base_datos import modelos as modelos_registrados
from app.modulos.estado.presentacion.rutas import router_estado
from app.modulos.carriles.presentacion.carril_router import (
    router as router_carriles,
)
from app.modulos.pagos.presentacion.pago_router import (
    router as router_pagos,
)

from app.modulos.accesos.presentacion.reingreso_router import (
    router as router_accesos,
)

from app.modulos.estancias.presentacion.estancia_router import (
    router as router_estancias,
)

configuracion = obtener_configuracion()

aplicacion = FastAPI(
    title=configuracion.nombre_aplicacion,
    version="0.1.0",
    docs_url="/docs",
)

aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aplicacion.include_router(
    router_estado,
    prefix=configuracion.prefijo_api,
)

aplicacion.include_router(
    router_carriles,
    prefix=configuracion.prefijo_api,
)

aplicacion.include_router(
    router_pagos,
    prefix=configuracion.prefijo_api,
)

aplicacion.include_router(
    router_accesos,
    prefix=configuracion.prefijo_api,
)

aplicacion.include_router(
    router_estancias,
    prefix=configuracion.prefijo_api,
)


@aplicacion.get('/', tags=["raiz"])
def raiz() -> dict[str, str]:
    return {
        "aplicacion": configuracion.nombre_aplicacion,
        "documentacion": "/docs",
    }