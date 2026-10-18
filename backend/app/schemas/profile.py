"""Esquemas del perfil (Pydantic)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=120)
    headline: str | None = Field(default=None, max_length=180)
    email: str | None = Field(default=None, max_length=180)
    phone: str | None = Field(default=None, max_length=40)
    location: str | None = Field(default=None, max_length=120)
    links: str | None = Field(default=None, max_length=300)
    summary: str | None = None
    skills: str | None = None
    cv_text: str | None = None


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    headline: str
    email: str
    phone: str
    location: str
    links: str
    summary: str
    skills: str
    cv_text: str
    updated_at: datetime | None = None


class CvUploadResult(BaseModel):
    filename: str
    chars: int
    profile: ProfileRead
