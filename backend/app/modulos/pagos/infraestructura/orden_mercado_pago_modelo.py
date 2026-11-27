
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class OrdenMercadoPagoModelo(Base):
    __tablename__ = "ordenes_mercado_pago"

    __table_args__ = (
        UniqueConstraint(
            "proveedor_order_id",
            name="uq_orden_mp_proveedor_order_id",
        ),
        UniqueConstraint(
            "external_reference",
            name="uq_orden_mp_external_reference",
        ),
        UniqueConstraint(
            "clave_idempotencia",
            name="uq_orden_mp_clave_idempotencia",
        ),
        CheckConstraint(
            "valor > 0",
            name="ck_orden_mp_valor_positivo",
        ),
        Index(
            "ix_orden_mp_cobro_id",
            "cobro_id",
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

    proveedor_order_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    external_reference: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="CREATING",
    )

    estado_detalle: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    valor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    moneda: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="COP",
    )

    checkout_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    clave_idempotencia: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    fecha_hora_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    fecha_hora_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
