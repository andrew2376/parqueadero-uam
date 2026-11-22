"""crear tabla accesos S113

Revision ID: 8945bdf49201
Revises: f3cd91c68d82
Create Date: 2026-11-22 18:41:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8945bdf49201'
down_revision: Union[str, Sequence[str], None] = 'f3cd91c68d82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'accesos',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('sede_id', sa.Uuid(), nullable=False),
        sa.Column('carril_id', sa.Uuid(), nullable=False),
        sa.Column('placa', sa.String(length=10), nullable=False),
        sa.Column('tipo_vehiculo', sa.String(length=10), nullable=False),
        sa.Column('fecha_ingreso', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_salida', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estado', sa.String(length=20), nullable=False),
        sa.Column('es_reingreso', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['sede_id'], ['sedes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['carril_id'], ['carriles.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_accesos_sede_id', 'accesos', ['sede_id'])
    op.create_index('ix_accesos_placa', 'accesos', ['placa'])
    op.create_index('ix_accesos_estado', 'accesos', ['estado'])


def downgrade() -> None:
    op.drop_index('ix_accesos_estado', table_name='accesos')
    op.drop_index('ix_accesos_placa', table_name='accesos')
    op.drop_index('ix_accesos_sede_id', table_name='accesos')
    op.drop_table('accesos')
