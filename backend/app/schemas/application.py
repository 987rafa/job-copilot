"""Esquemas de postulaciones y resultados de análisis (Pydantic)."""
import json
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.application import APPLICATION_STATUSES


class AnalysisResult(BaseModel):
    """Resultado del análisis de una oferta frente al perfil."""

    fit_score: int = Field(default=0, ge=0, le=100)
    summary: str = ""
    strengths: list[str] = []
    gaps: list[str] = []
    keywords: list[str] = []


class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=140)
    role: str = Field(min_length=1, max_length=180)
    source: str = Field(default="", max_length=80)
    url: str = Field(default="", max_length=500)
    job_text: str = ""
    notes: str = ""
    next_followup: date | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=140)
    role: str | None = Field(default=None, min_length=1, max_length=180)
    source: str | None = Field(default=None, max_length=80)
    url: str | None = Field(default=None, max_length=500)
    job_text: str | None = None
    notes: str | None = None
    status: str | None = None
    next_followup: date | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in APPLICATION_STATUSES:
            raise ValueError(f"Estado inválido: {value}. Válidos: {', '.join(APPLICATION_STATUSES)}")
        return value


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role: str
    source: str
    url: str
    job_text: str
    status: str
    fit_score: int | None = None
    analysis: AnalysisResult | None = None
    notes: str
    next_followup: date | None = None
    applied_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("analysis", mode="before")
    @classmethod
    def parse_analysis(cls, value):
        # SQLAlchemy ya devuelve un dict para la columna JSON; aceptamos texto por si acaso.
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return None
        return value


class ApplicationList(BaseModel):
    items: list[ApplicationRead]
    total: int
