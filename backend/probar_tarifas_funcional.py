from datetime import datetime
from decimal import Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

# Registrar todos los modelos SQLAlchemy, incluyendo SedeModelo.
from app.infraestructura.base_datos.conexion import FabricaSesiones
from app.modulos.tarifas.aplicacion.calcular_tarifa import CalcularTarifa
from app.modulos.tarifas.aplicacion.configurar_tarifa import ConfigurarTarifa
from app.modulos.tarifas.dominio.franja_horaria import FranjaHoraria
from app.modulos.tarifas.infraestructura.tarifa_modelo import TarifaModelo
from app.modulos.tarifas.infraestructura.tarifa_repositorio_sqlalchemy import (
    TarifaRepositorioSQLAlchemy,
)

SEDE_ID = UUID("03793b27-4b34-42ea-9bb0-28f8bc5b330d")
ZONA = "America/Bogota"

ids_prueba = []


def verificar(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise AssertionError(mensaje)

    print(f"OK: {mensaje}")


sesion = FabricaSesiones()

try:
    repositorio = TarifaRepositorioSQLAlchemy(sesion)

    configurar = ConfigurarTarifa(repositorio)
    calcular = CalcularTarifa(repositorio)

    print("\n========== PRUEBAS FUNCIONALES S112 ==========\n")

    # Verificar que la sede exista.
    from app.modulos.sedes.infraestructura.sede_modelo import SedeModelo

    sede = sesion.get(SedeModelo, SEDE_ID)

    verificar(sede is not None, "Sede Principal UAM encontrada")

    # Comprobar que no existan tarifas previas.
    tarifas_existentes = repositorio.listar_por_sede(SEDE_ID)

    verificar(
        len(tarifas_existentes) == 0,
        "La sede no tiene tarifas previas; se puede probar sin sobrescribir datos",
    )

    # 1. Configurar tarifa de carro.
    carro = configurar.ejecutar(
        sede_id=SEDE_ID,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("5000"),
        tarifa_nocturna=Decimal("3000"),
    )

    ids_prueba.append(carro.id)

    verificar(
        carro.tarifa_diurna == Decimal("5000"),
        "Configuración de tarifa diurna para CARRO",
    )

    verificar(
        carro.tarifa_nocturna == Decimal("3000"),
        "Configuración de tarifa nocturna para CARRO",
    )

    # 2. Configurar motocicleta gratuita.
    moto = configurar.ejecutar(
        sede_id=SEDE_ID,
        tipo_vehiculo="MOTO",
        tarifa_diurna=Decimal("0"),
        tarifa_nocturna=Decimal("0"),
    )

    ids_prueba.append(moto.id)

    verificar(
        moto.tarifa_diurna == Decimal("0") and moto.tarifa_nocturna == Decimal("0"),
        "Configuración de MOTO gratuita",
    )

    # 3. Consultar las tarifas desde PostgreSQL.
    carro_bd = repositorio.buscar_por_sede_y_tipo(
        SEDE_ID,
        "CARRO",
    )

    moto_bd = repositorio.buscar_por_sede_y_tipo(
        SEDE_ID,
        "MOTO",
    )

    verificar(
        carro_bd is not None and carro_bd.tarifa_diurna == Decimal("5000"),
        "Consulta de CARRO en PostgreSQL",
    )

    verificar(
        moto_bd is not None and moto_bd.tarifa_diurna == Decimal("0"),
        "Consulta de MOTO en PostgreSQL",
    )

    # 4. Calcular tarifa diurna: 10:00.
    resultado_dia = calcular.ejecutar(
        sede_id=SEDE_ID,
        tipo_vehiculo="CARRO",
        fecha_hora=datetime(
            2026,
            11,
            23,
            10,
            0,
            tzinfo=ZoneInfo(ZONA),
        ),
        zona_horaria=ZONA,
    )

    verificar(
        resultado_dia["franja_horaria"] == FranjaHoraria.DIURNA.value,
        "Identificación de franja DIURNA a las 10:00",
    )

    verificar(
        resultado_dia["valor_tarifa"] == Decimal("5000"),
        "Cálculo de $5.000 para CARRO en horario diurno",
    )

    # 5. Calcular tarifa nocturna: 20:00.
    resultado_noche = calcular.ejecutar(
        sede_id=SEDE_ID,
        tipo_vehiculo="CARRO",
        fecha_hora=datetime(
            2026,
            11,
            23,
            20,
            0,
            tzinfo=ZoneInfo(ZONA),
        ),
        zona_horaria=ZONA,
    )

    verificar(
        resultado_noche["franja_horaria"] == FranjaHoraria.NOCTURNA.value,
        "Identificación de franja NOCTURNA a las 20:00",
    )

    verificar(
        resultado_noche["valor_tarifa"] == Decimal("3000"),
        "Cálculo de $3.000 para CARRO en horario nocturno",
    )

    # 6. Actualizar tarifa sin duplicar el registro.
    carro_actualizado = configurar.ejecutar(
        sede_id=SEDE_ID,
        tipo_vehiculo="CARRO",
        tarifa_diurna=Decimal("6000"),
        tarifa_nocturna=Decimal("4000"),
    )

    verificar(
        carro_actualizado.tarifa_diurna == Decimal("6000"),
        "Actualización de tarifa diurna",
    )

    verificar(
        carro_actualizado.id == carro.id,
        "Actualización conserva el ID original",
    )

    cantidad_carros = (
        sesion.query(TarifaModelo)
        .filter(
            TarifaModelo.sede_id == SEDE_ID,
            TarifaModelo.tipo_vehiculo == "CARRO",
        )
        .count()
    )

    verificar(
        cantidad_carros == 1,
        "Actualizar no genera registros duplicados",
    )

    # 7. Rechazar configuraciones inválidas.
    casos_invalidos = [
        ("CARRO", "5000", "5000", "Tarifas iguales"),
        ("CARRO", "3000", "5000", "Nocturna superior"),
        ("CARRO", "3000", "-500", "Tarifa negativa"),
    ]

    for tipo, diurna, nocturna, descripcion in casos_invalidos:
        try:
            configurar.ejecutar(
                sede_id=SEDE_ID,
                tipo_vehiculo=tipo,
                tarifa_diurna=Decimal(diurna),
                tarifa_nocturna=Decimal(nocturna),
            )
        except ValueError:
            print(f"OK: Rechazo de {descripcion}")
        else:
            raise AssertionError(f"La configuración inválida fue aceptada: {descripcion}")

    # 8. Mostrar tarifas configuradas.
    tarifas = repositorio.listar_por_sede(SEDE_ID)

    print("\nTarifas registradas durante la prueba:")

    for tarifa in tarifas:
        print(
            f"{tarifa.tipo_vehiculo}: "
            f"Diurna ${tarifa.tarifa_diurna} | "
            f"Nocturna ${tarifa.tarifa_nocturna}"
        )

    print("\nTODAS LAS PRUEBAS FUNCIONALES PASARON.")

finally:
    # El repositorio realiza commit() en cada guardado.
    # Por eso se eliminan exclusivamente los IDs creados por esta prueba.
    try:
        if ids_prueba:
            sesion.rollback()

            sesion.query(TarifaModelo).filter(TarifaModelo.id.in_(ids_prueba)).delete(
                synchronize_session=False
            )

            sesion.commit()

            print("\nLimpieza de registros de prueba completada.")

    finally:
        sesion.close()
