from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base
from app.modulos.accesos.dominio.ingreso import EstadoAcceso
from app.modulos.vehiculos.dominio.vehiculo import TipoVehiculo


class AccesoModelo(Base):
    __tablename__ = "accesos"

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    sede_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    carril_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("carriles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    placa: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    tipo_vehiculo: Mapped[TipoVehiculo] = mapped_column(
        SAEnum(TipoVehiculo, name="tipo_vehiculo_enum", native_enum=False),
        nullable=False,
    )
    fecha_ingreso: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    fecha_salida: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    estado: Mapped[EstadoAcceso] = mapped_column(
        SAEnum(EstadoAcceso, name="estado_acceso_enum", native_enum=False),
        nullable=False,
        default=EstadoAcceso.ACTIVO,
        index=True,
    )
    es_reingreso: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
