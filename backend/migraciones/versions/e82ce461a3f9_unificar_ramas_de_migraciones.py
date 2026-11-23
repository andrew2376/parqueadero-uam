"""unificar ramas de migraciones

Revision ID: e82ce461a3f9
Revises: 5d1bcf89fb55, aa283e86ea72
Create Date: 2026-11-23 14:27:29.364239

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "e82ce461a3f9"
down_revision: str | Sequence[str] | None = ("5d1bcf89fb55", "aa283e86ea72")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
