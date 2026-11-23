import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class TarifaModelo(Base):
    __tablename__ = "tarifas"

    __table_args__ = (
        UniqueConstraint(
            "sede_id",
            "tipo_vehiculo",
            name="uq_tarifa_sede_tipo_vehiculo",
        ),
        CheckConstraint(
            "tipo_vehiculo IN ('CARRO', 'MOTO')",
            name="ck_tarifa_tipo_vehiculo",
        ),
        CheckConstraint(
            "tarifa_diurna >= 0 AND tarifa_nocturna >= 0",
            name="ck_tarifa_valores_no_negativos",
        ),
        CheckConstraint(
            "(tipo_vehiculo = 'MOTO' AND tarifa_diurna = 0 "
            "AND tarifa_nocturna = 0) "
            "OR tarifa_nocturna < tarifa_diurna",
            name="ck_tarifa_nocturna_menor_diurna",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    sede_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    tipo_vehiculo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    tarifa_diurna: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )

    tarifa_nocturna: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0"),
    )

    activa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
