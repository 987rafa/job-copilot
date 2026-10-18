"""Postulaciones de empleo (oferta + estado + análisis de IA)."""
from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Estados del tablero de postulaciones
APPLICATION_STATUSES = ("guardada", "aplicada", "entrevista", "oferta", "rechazada")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str] = mapped_column(String(140), index=True)
    role: Mapped[str] = mapped_column(String(180))
    source: Mapped[str] = mapped_column(String(80), default="")  # LinkedIn, portal, referido…
    url: Mapped[str] = mapped_column(String(500), default="")
    job_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="guardada", index=True)
    fit_score: Mapped[int | None] = mapped_column(nullable=True)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    next_followup: Mapped[date | None] = mapped_column(Date, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
