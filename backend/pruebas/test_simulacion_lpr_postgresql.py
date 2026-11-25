from datetime import UTC, datetime, time, timedelta
from secrets import token_urlsafe
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from test_usuarios_postgresql import conexion_postgresql as conexion_postgresql


def test_capturas_lpr_autenticadas_y_persistidas(conexion_postgresql, monkeypatch):
    from app.infraestructura.base_datos.conexion import obtener_sesion
    from app.main import aplicacion
    from app.modulos.autenticacion.infraestructura.password_hasher_argon2 import (
        PasswordHasherArgon2,
    )
    from app.modulos.autenticacion.infraestructura.usuario_modelo import UsuarioModelo
    from app.modulos.carriles.infraestructura.carril_modelo import CarrilModelo
    from app.modulos.cobros.infraestructura.cobro_modelo import CobroModelo
    from app.modulos.estancias.infraestructura.estancia_modelo import EstanciaModelo
    from app.modulos.eventos_lectura.infraestructura.evento_lectura_modelo import (
        EventoLecturaModelo,
    )
    from app.modulos.pagos.infraestructura.pago_modelo import PagoModelo
    from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo
    from app.modulos.tarifas.infraestructura.tarifa_modelo import TarifaModelo

    def sesion_prueba():
        with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
            yield sesion

    sede_id, carril_id = uuid4(), uuid4()
    password = token_urlsafe(24)
    usuarios = {rol: f"lpr-{uuid4().hex[:12]}" for rol in ("OPERADOR", "ADMINISTRADOR")}
    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        sesion.add(
            SedeModelo(
                id=sede_id,
                nombre=f"Prueba LPR {sede_id}",
                zona_horaria="America/Bogota",
                inicio_dia_operativo=time(6),
                cupos_carro=1,
                cupos_moto=1,
            )
        )
        sesion.flush()
        sesion.add(CarrilModelo(id=carril_id, sede_id=sede_id, nombre="Entrada", tipo="MIXTO"))
        sesion.add(
            TarifaModelo(
                sede_id=sede_id,
                tipo_vehiculo="CARRO",
                tarifa_diurna=3000,
                tarifa_nocturna=2000,
                vigencia_desde=datetime.now(UTC) - timedelta(days=1),
            )
        )
        for rol, username in usuarios.items():
            sesion.add(
                UsuarioModelo(
                    username=username,
                    nombre_completo="Prueba LPR",
                    password_hash=PasswordHasherArgon2().hashear(password),
                    rol=rol,
                )
            )
        sesion.commit()

    monkeypatch.setitem(aplicacion.dependency_overrides, obtener_sesion, sesion_prueba)
    prefijo = "/api/v1/lecturas-lpr"
    ruta = f"{prefijo}/simulacion"
    params = {"carril_id": str(carril_id)}
    capturas = {}
    tokens = {}
    with TestClient(aplicacion) as cliente:
        for headers in ({}, {"Authorization": "Bearer invalido"}):
            assert cliente.post(ruta, params=params, headers=headers).status_code == 401
            assert (
                cliente.post(
                    f"{prefijo}/automatica",
                    params=params,
                    headers=headers,
                ).status_code
                == 401
            )
            assert (
                cliente.post(
                    f"{prefijo}/manual",
                    json={**params, "placa": "ABC123"},
                    headers=headers,
                ).status_code
                == 401
            )

        for username in usuarios.values():
            ingreso = cliente.post(
                "/api/v1/auth/login",
                json={"username": username, "password": password},
            )
            assert ingreso.status_code == 200
            headers = tokens[username] = {"Authorization": f"Bearer {ingreso.json()['token']}"}
            for escenario, estado, placa, tipo, confianza in (
                ("alta", "EXITOSA", "ABC123", "CARRO", 95),
                ("baja", "BAJA_CONFIANZA", "DEF45A", "MOTO", 55),
                ("sin-lectura", "FALLIDA", None, None, 0),
            ):
                respuesta = cliente.post(
                    ruta,
                    params={**params, "escenario": escenario, "direccion": "SALIDA"},
                    headers=headers,
                )
                assert respuesta.status_code == 201, respuesta.text
                datos = respuesta.json()
                assert datos["direccion"] == "SALIDA"
                assert (
                    datos["estado"],
                    datos["placa"],
                    datos["tipo_vehiculo"],
                    datos["confianza"],
                ) == (estado, placa, tipo, confianza)
                assert datos["requiere_confirmacion_manual"] is (escenario != "alta")
                assert UUID(datos["id"]) not in capturas
                capturas[UUID(datos["id"])] = datos

        assert (
            cliente.post(ruta, params={**params, "escenario": "otro"}, headers=headers).status_code
            == 422
        )
        assert (
            cliente.post(ruta, params={"carril_id": str(uuid4())}, headers=headers).status_code
            == 404
        )

    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        eventos = sesion.scalars(
            select(EventoLecturaModelo).where(
                EventoLecturaModelo.carril_id == carril_id,
            )
        ).all()
        assert {evento.id for evento in eventos} == capturas.keys()
        for evento in eventos:
            datos = capturas[evento.id]
            assert evento.sede_id == UUID(datos["sede_id"]) == sede_id
            assert evento.carril_id == UUID(datos["carril_id"]) == carril_id
            assert evento.fecha_hora == datetime.fromisoformat(datos["fecha_hora"])
            assert evento.estado == datos["estado"]
            assert evento.placa == datos["placa"]
            assert float(evento.confianza) == datos["confianza"]
            assert evento.origen == datos["origen"] == "AUTOMATICO"
        assert (
            sesion.scalar(
                select(EstanciaModelo.id).where(
                    EstanciaModelo.sede_id == sede_id,
                )
            )
            is None
        )

    with TestClient(aplicacion) as cliente:
        api = "/api/v1"
        operador = tokens[usuarios["OPERADOR"]]
        admin = tokens[usuarios["ADMINISTRADOR"]]
        acceso = {"sede_id": str(sede_id), "placa": "ABC123"}

        def cupos_carro():
            respuesta = cliente.get(f"{api}/cupos/sede/{sede_id}", headers=admin)
            assert respuesta.status_code == 200, respuesta.text
            return next(c["disponibles"] for c in respuesta.json() if c["tipo_vehiculo"] == "CARRO")

        def salida():
            respuesta = cliente.post(f"{api}/estancias/salida", json=acceso, headers=operador)
            assert respuesta.status_code == 200, respuesta.text
            return respuesta.json()

        assert not salida()["autorizado"]
        assert cupos_carro() == 1
        captura = cliente.post(
            ruta,
            params={**params, "direccion": "ENTRADA", "escenario": "baja"},
            headers=operador,
        )
        assert captura.status_code == 201 and captura.json()["requiere_confirmacion_manual"]
        assert (
            cliente.post(
                f"{prefijo}/manual", json={**params, "placa": "123456"}, headers=operador
            ).status_code
            == 422
        )
        manual = cliente.post(
            f"{prefijo}/manual", json={**params, "placa": "abc-123"}, headers=operador
        )
        assert manual.status_code == 201 and manual.json()["placa"] == acceso["placa"]
        ingreso = cliente.post(
            f"{api}/accesos/ingreso", json={**params, **acceso}, headers=operador
        )
        assert ingreso.status_code == 200 and ingreso.json()["autorizado"], ingreso.text
        assert cupos_carro() == 0
        salida_captura = cliente.post(
            ruta, params={**params, "direccion": "SALIDA"}, headers=operador
        )
        assert (
            salida_captura.status_code == 201 and salida_captura.json()["placa"] == acceso["placa"]
        )
        pendiente = salida()
        assert not pendiente["autorizado"] and "pendiente" in pendiente["motivo"]
        assert cupos_carro() == 0
        with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
            cobro = sesion.get(CobroModelo, UUID(pendiente["cobro_id"]))
            assert cobro is not None
            valor = str(cobro.valor_tarifa)
        pago = cliente.post(
            f"{api}/pagos/efectivo",
            headers=admin,
            json={
                "cobro_id": pendiente["cobro_id"],
                "valor": valor,
                "clave_idempotencia": str(uuid4()),
            },
        )
        assert pago.status_code == 200, pago.text
        autorizada = salida()
        assert autorizada["autorizado"] and autorizada["decision_barrera"] == "AUTORIZAR"
        assert cupos_carro() == 1

    with Session(conexion_postgresql, join_transaction_mode="create_savepoint") as sesion:
        estancia = sesion.get(EstanciaModelo, UUID(autorizada["estancia_id"]))
        assert estancia is not None and estancia.fecha_hora_salida is not None
        assert sesion.get(PagoModelo, UUID(pago.json()["id"])) is not None
        for respuesta in (captura, manual, salida_captura):
            evento = sesion.get(EventoLecturaModelo, UUID(respuesta.json()["id"]))
            assert evento is not None and evento.carril_id == carril_id
