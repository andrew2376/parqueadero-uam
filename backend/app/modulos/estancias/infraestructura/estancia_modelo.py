import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class EstanciaModelo(Base):
    __tablename__ = "estancias"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    sede_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    placa: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    tipo_vehiculo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    fecha_hora_entrada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_hora_salida: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="DENTRO",
    )
