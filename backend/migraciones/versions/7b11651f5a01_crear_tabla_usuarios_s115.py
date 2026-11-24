"""Crear la tabla de usuarios de autenticación S115."""

import sqlalchemy as sa
from alembic import op

revision = "7b11651f5a01"
down_revision = "3bdca28cefbc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("nombre_completo", sa.String(150), nullable=False),
        sa.Column("rol", sa.String(16), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_usuarios"),
        sa.UniqueConstraint("username", name="uq_usuarios_username"),
        sa.CheckConstraint(
            "username <> '' AND username = lower(trim(username))",
            name="ck_usuarios_username_canonico",
        ),
        sa.CheckConstraint("rol IN ('OPERADOR', 'ADMINISTRADOR')", name="ck_usuarios_rol"),
    )


def downgrade() -> None:
    op.drop_table("usuarios")
