"""unificar ramas de migraciones

Revision ID: 3bdca28cefbc
Revises: 059efbca09f6, 4dec131a35cb
Create Date: 2026-11-24 11:44:21.960349

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "3bdca28cefbc"
down_revision: str | Sequence[str] | None = ("059efbca09f6", "4dec131a35cb")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
