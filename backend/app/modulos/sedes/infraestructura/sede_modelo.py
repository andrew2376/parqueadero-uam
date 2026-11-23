
from uuid import UUID, uuid4

from sqlalchemy import Integer, String, Time, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infraestructura.base_datos.conexion import Base


class SedeModelo(Base):
    __tablename__ = "sedes"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    zona_horaria: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    inicio_dia_operativo: Mapped[Time] = mapped_column(
        Time,
        nullable=False,
    )

    cupos_carro: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    cupos_moto: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
