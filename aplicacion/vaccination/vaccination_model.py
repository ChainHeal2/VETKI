"""Modelo SQLAlchemy del historial de vacunación.

La aplicación histórica usa SQL directo; este modelo permite reutilizar el
contrato ORM en nuevas integraciones sin cambiar la conexión de producción.
"""
from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Vaccination(Base):
    __tablename__ = "vaccinations"
    __table_args__ = {"schema": "vetki"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pet_id: Mapped[int] = mapped_column(
        ForeignKey("vetki.pet_data.pet_id", ondelete="CASCADE"), nullable=False
    )
    vaccine_name: Mapped[str] = mapped_column(String(120), nullable=False)
    application_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    lot_number: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    veterinarian_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
