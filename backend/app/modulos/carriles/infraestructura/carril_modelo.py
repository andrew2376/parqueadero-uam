
import uuid

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class CarrilModelo(Base):
    __tablename__ = "carriles"

    __table_args__ = (
        UniqueConstraint(
            "sede_id",
            "nombre",
            name="uq_carril_sede_nombre",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    sede_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
