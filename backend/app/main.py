
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.configuracion import obtener_configuracion
from app.infraestructura.base_datos import modelos as modelos_registrados  # noqa: F401

from app.modulos.accesos.presentacion.ingreso_router import (
    router as router_ingreso,
)
from app.modulos.accesos.presentacion.reingreso_router import (
    router as router_accesos,
)
from app.modulos.auditoria.presentacion.auditoria_router import (
    router as router_auditoria,
)
from app.modulos.autenticacion.presentacion.auth_router import (
    router as router_auth,
)
from app.modulos.carriles.presentacion.carril_router import (
    router as router_carriles,
)
from app.modulos.cupos.presentacion.cupo_router import (
    router as router_cupos,
)
from app.modulos.estado.presentacion.rutas import router_estado
from app.modulos.estancias.presentacion.estancia_router import (
    router as router_estancias,
)
from app.modulos.eventos_lectura.presentacion.evento_lectura_router import (
    router as router_eventos_lectura,
)
from app.modulos.pagos.presentacion.pago_router import (
    router as router_pagos,
)
from app.modulos.reconocimiento_placas.presentacion.lpr_router import (
    router as router_lpr,
)
from app.modulos.reconocimiento_placas.presentacion.validacion_manual_router import (
    router as router_validacion_manual_lpr,
)
from app.modulos.tarifas.presentacion.tarifa_router import (
    router_tarifas,
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


# Estado
aplicacion.include_router(
    router_estado,
    prefix=configuracion.prefijo_api,
)


# Carriles
aplicacion.include_router(
    router_carriles,
    prefix=configuracion.prefijo_api,
)


# Tarifas
aplicacion.include_router(
    router_tarifas,
    prefix=configuracion.prefijo_api,
)


# Cupos
aplicacion.include_router(
    router_cupos,
    prefix=configuracion.prefijo_api,
)


# Pagos
aplicacion.include_router(
    router_pagos,
    prefix=configuracion.prefijo_api,
)


# Accesos
aplicacion.include_router(
    router_accesos,
    prefix=configuracion.prefijo_api,
)


# Estancias
aplicacion.include_router(
    router_estancias,
    prefix=configuracion.prefijo_api,
)


# Ingreso
aplicacion.include_router(
    router_ingreso,
    prefix=configuracion.prefijo_api,
)


# Autenticación
aplicacion.include_router(
    router_auth,
    prefix=configuracion.prefijo_api,
)


# Reconocimiento de placas (LPR)
aplicacion.include_router(
    router_lpr,
    prefix=configuracion.prefijo_api,
)


# Validación manual de placas
aplicacion.include_router(
    router_validacion_manual_lpr,
    prefix=configuracion.prefijo_api,
)


# Eventos de lectura
aplicacion.include_router(
    router_eventos_lectura,
    prefix=configuracion.prefijo_api,
)


# Auditoría
aplicacion.include_router(
    router_auditoria,
    prefix=configuracion.prefijo_api,
)


@aplicacion.get("/", tags=["raiz"])
def raiz() -> dict[str, str]:
    return {
        "aplicacion": configuracion.nombre_aplicacion,
        "documentacion": "/docs",
    }
