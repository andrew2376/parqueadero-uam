
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class PagoModelo(Base):
    __tablename__ = "pagos"

    __table_args__ = (
        UniqueConstraint(
            "cobro_id",
            name="uq_pago_cobro",
        ),
        UniqueConstraint(
            "clave_idempotencia",
            name="uq_pago_clave_idempotencia",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    cobro_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cobros.id", ondelete="RESTRICT"),
        nullable=False,
    )

    medio_pago: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="EFECTIVO",
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_hora_pago: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    clave_idempotencia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
