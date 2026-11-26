from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class UsuarioModelo(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_usuarios"),
        UniqueConstraint("username", name="uq_usuarios_username"),
        CheckConstraint(
            "username <> '' AND username = lower(trim(username))",
            name="ck_usuarios_username_canonico",
        ),
        CheckConstraint("rol IN ('OPERADOR', 'ADMINISTRADOR')", name="ck_usuarios_rol"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    rol: Mapped[str] = mapped_column(String(16), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
