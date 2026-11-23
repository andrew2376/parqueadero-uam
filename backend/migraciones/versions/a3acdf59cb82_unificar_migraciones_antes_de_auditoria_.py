"""unificar migraciones antes de auditoria S209

Revision ID: a3acdf59cb82
Revises: 05a3d6616f50, f3e3762a3082
Create Date: 2026-11-23 18:35:50.567522

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3acdf59cb82'
down_revision: Union[str, Sequence[str], None] = ('05a3d6616f50', 'f3e3762a3082')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
