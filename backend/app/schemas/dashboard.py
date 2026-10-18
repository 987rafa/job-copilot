"""Esquemas del panel (dashboard)."""
from pydantic import BaseModel

from app.schemas.application import ApplicationRead


class DashboardRead(BaseModel):
    total: int
    active: int
    by_status: dict[str, int]
    avg_fit: float | None = None
    applied_this_week: int
    upcoming_followups: list[ApplicationRead]
    recent: list[ApplicationRead]
    llm: str  # proveedor de IA activo ("heuristic" si no hay claves configuradas)
