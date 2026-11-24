
"""Versionar tarifas y agregar periodos de vigencia - S206."""

from alembic import op
import sqlalchemy as sa


revision = "s206_tarifas_versionadas"
down_revision = ("05a3d6616f50", "f3e3762a3082")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eliminar la restricción que impedía tener varias versiones
    # para una misma sede y tipo de vehículo.
    op.drop_constraint(
        "uq_tarifa_sede_tipo_vehiculo",
        "tarifas",
        type_="unique",
    )

    # Agregar el número de versión.
    # Las tarifas existentes reciben la versión 1.
    op.add_column(
        "tarifas",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    # Agregar fecha inicial de vigencia.
    # Los registros existentes reciben la fecha de ejecución.
    op.add_column(
        "tarifas",
        sa.Column(
            "vigencia_desde",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # La fecha final puede ser nula si la tarifa sigue vigente.
    op.add_column(
        "tarifas",
        sa.Column(
            "vigencia_hasta",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Cada versión debe ser única por sede y tipo de vehículo.
    op.create_unique_constraint(
        "uq_tarifa_sede_tipo_version",
        "tarifas",
        ["sede_id", "tipo_vehiculo", "version"],
    )

    # Validar que la versión sea positiva.
    op.create_check_constraint(
        "ck_tarifa_version_positiva",
        "tarifas",
        "version >= 1",
    )

    # La fecha final debe ser posterior a la fecha inicial.
    op.create_check_constraint(
        "ck_tarifa_vigencia_valida",
        "tarifas",
        "vigencia_hasta IS NULL OR vigencia_hasta > vigencia_desde",
    )

    # Índice para consultar tarifas por sede, tipo y vigencia.
    op.create_index(
        "ix_tarifa_busqueda_vigencia",
        "tarifas",
        [
            "sede_id",
            "tipo_vehiculo",
            "vigencia_desde",
            "vigencia_hasta",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tarifa_busqueda_vigencia",
        table_name="tarifas",
    )

    op.drop_constraint(
        "ck_tarifa_vigencia_valida",
        "tarifas",
        type_="check",
    )

    op.drop_constraint(
        "ck_tarifa_version_positiva",
        "tarifas",
        type_="check",
    )

    op.drop_constraint(
        "uq_tarifa_sede_tipo_version",
        "tarifas",
        type_="unique",
    )

    op.drop_column("tarifas", "vigencia_hasta")
    op.drop_column("tarifas", "vigencia_desde")
    op.drop_column("tarifas", "version")

    # Restaurar la restricción anterior.
    # Esto requiere que no existan varias versiones por sede y tipo.
    op.create_unique_constraint(
        "uq_tarifa_sede_tipo_vehiculo",
        "tarifas",
        ["sede_id", "tipo_vehiculo"],
    )
