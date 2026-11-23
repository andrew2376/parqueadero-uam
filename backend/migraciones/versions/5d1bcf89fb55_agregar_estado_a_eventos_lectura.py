
"""agregar estado a eventos lectura

Revision ID: 5d1bcf89fb55
Revises: 50bfe64d71cb
Create Date: 2026-11-22 22:03:52.736947

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5d1bcf89fb55'
down_revision: Union[str, Sequence[str], None] = '50bfe64d71cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar estado inicialmente como nullable.
    op.add_column(
        'eventos_lectura',
        sa.Column('estado', sa.String(length=20), nullable=True)
    )

    # Asignar EXITOSA a los eventos que ya estaban registrados.
    op.execute(
        "UPDATE eventos_lectura SET estado = 'EXITOSA' WHERE estado IS NULL"
    )

    # Hacer que estado sea obligatorio.
    op.alter_column(
        'eventos_lectura',
        'estado',
        existing_type=sa.String(length=20),
        nullable=False
    )

    # Permitir eventos sin placa reconocida.
    op.alter_column(
        'eventos_lectura',
        'placa',
        existing_type=sa.VARCHAR(length=10),
        nullable=True
    )


def downgrade() -> None:
    # Restaurar la obligatoriedad de placa.
    # Esta operación requiere que no existan eventos con placa NULL.
    op.alter_column(
        'eventos_lectura',
        'placa',
        existing_type=sa.VARCHAR(length=10),
        nullable=False
    )

    op.drop_column('eventos_lectura', 'estado')
