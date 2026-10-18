"""Esquemas de las funciones de IA (análisis y borradores)."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.application import AnalysisResult


class AnalyzeRequest(BaseModel):
    job_text: str = Field(min_length=30, description="Texto completo de la oferta de trabajo")
    company: str = Field(default="", max_length=140)
    role: str = Field(default="", max_length=180)
    source: str = Field(default="", max_length=80)
    url: str = Field(default="", max_length=500)
    save: bool = False


class AnalyzeResponse(BaseModel):
    analysis: AnalysisResult
    application_id: int | None = None


DraftKind = Literal["carta", "mensaje", "seguimiento"]
DraftLanguage = Literal["es", "en"]
DraftTone = Literal["profesional", "cercano", "entusiasta", "directo"]


class DraftRequest(BaseModel):
    application_id: int | None = None
    job_text: str = ""
    kind: DraftKind = "carta"
    language: DraftLanguage = "es"
    tone: DraftTone = "profesional"
    extra_notes: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def require_source(self):
        if self.application_id is None and len(self.job_text.strip()) < 20:
            raise ValueError("Envía el texto de la oferta o el id de una postulación guardada")
        return self


class DraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int | None = None
    kind: str
    language: str
    tone: str
    content: str
    created_at: datetime | None = None
