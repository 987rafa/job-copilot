"""Salud del servicio."""
from fastapi import APIRouter

from app.core.config import settings
from app.services.llm import resolve_provider

router = APIRouter(tags=["salud"])


@router.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.version,
        "llm": resolve_provider() or "heuristic",
    }
