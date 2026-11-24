"""Crear tabla tarifas S112.

Revision ID: f3e3762a3082
Revises: e82ce461a3f9
Create Date: 2026-11-23 14:30:38.646156
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# Identificadores de revisión de Alembic.
revision: str = "f3e3762a3082"
down_revision: str | Sequence[str] | None = "e82ce461a3f9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crear la tabla de configuración de tarifas."""

    op.create_table(
        "tarifas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sede_id", sa.Uuid(), nullable=False),
        sa.Column("tipo_vehiculo", sa.String(length=20), nullable=False),
        sa.Column(
            "tarifa_diurna",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "tarifa_nocturna",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "(tipo_vehiculo = 'MOTO' "
            "AND tarifa_diurna = 0 "
            "AND tarifa_nocturna = 0) "
            "OR tarifa_nocturna < tarifa_diurna",
            name="ck_tarifa_nocturna_menor_diurna",
        ),
        sa.CheckConstraint(
            "tipo_vehiculo IN ('CARRO', 'MOTO')",
            name="ck_tarifa_tipo_vehiculo",
        ),
        sa.CheckConstraint(
            "tarifa_diurna >= 0 AND tarifa_nocturna >= 0",
            name="ck_tarifa_valores_no_negativos",
        ),
        sa.ForeignKeyConstraint(
            ["sede_id"],
            ["sedes.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "sede_id",
            "tipo_vehiculo",
            name="uq_tarifa_sede_tipo_vehiculo",
        ),
    )


def downgrade() -> None:
    """Eliminar la tabla de tarifas."""

    op.drop_table("tarifas")
