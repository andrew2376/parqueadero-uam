"""unificar ramas de migraciones

Revision ID: 3bdca28cefbc
Revises: 059efbca09f6, 4dec131a35cb
Create Date: 2026-11-24 11:44:21.960349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bdca28cefbc'
down_revision: Union[str, Sequence[str], None] = ('059efbca09f6', '4dec131a35cb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
