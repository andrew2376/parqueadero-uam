import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class AuditoriaModelo(Base):
    __tablename__ = "auditorias"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    accion: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entidad: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entidad_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    detalles: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
