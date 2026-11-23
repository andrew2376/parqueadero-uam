"""unificar migraciones estancias y eventos

Revision ID: 05a3d6616f50
Revises: 5d1bcf89fb55, aa283e86ea72
Create Date: 2026-11-23 15:14:46.255795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05a3d6616f50'
down_revision: Union[str, Sequence[str], None] = ('5d1bcf89fb55', 'aa283e86ea72')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
