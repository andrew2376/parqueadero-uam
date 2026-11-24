"""agregar_snapshot_tarifa_cobros

Revision ID: 4dec131a35cb
Revises: s206_tarifas_versionadas
Create Date: 2026-11-23 19:00:57.453534

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dec131a35cb"
down_revision: str | Sequence[str] | None = "s206_tarifas_versionadas"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Agrega el snapshot de tarifa a los cobros."""

    op.add_column(
        "cobros",
        sa.Column("tarifa_id", sa.Uuid(), nullable=False),
    )

    op.add_column(
        "cobros",
        sa.Column("version_tarifa", sa.Integer(), nullable=False),
    )

    op.create_foreign_key(
        "fk_cobros_tarifa_id_tarifas",
        "cobros",
        "tarifas",
        ["tarifa_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Revierte los campos del snapshot de tarifa."""

    op.drop_constraint(
        "fk_cobros_tarifa_id_tarifas",
        "cobros",
        type_="foreignkey",
    )

    op.drop_column("cobros", "version_tarifa")
    op.drop_column("cobros", "tarifa_id")
