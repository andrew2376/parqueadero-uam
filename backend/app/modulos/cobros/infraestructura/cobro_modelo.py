
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class CobroModelo(Base):
    __tablename__ = "cobros"

    __table_args__ = (
        UniqueConstraint(
            "placa",
            "sede_id",
            "dia_operativo",
            name="uq_cobro_placa_sede_dia",
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

    placa: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    dia_operativo: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    tarifa_aplicada: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    valor_tarifa: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    fecha_hora_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
