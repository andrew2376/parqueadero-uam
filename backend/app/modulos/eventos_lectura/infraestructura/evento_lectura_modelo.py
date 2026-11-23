from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class EventoLecturaModelo(Base):
    __tablename__ = "eventos_lectura"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    sede_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    carril_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("carriles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    placa: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    confianza: Mapped[float] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    origen: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
