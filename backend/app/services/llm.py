"""Capa de IA agnóstica de proveedor.

Soporta cualquier API compatible con OpenAI (OpenAI, Groq, OpenRouter, Together,
Ollama, LM Studio, OmniRoute…) y Google Gemini. Si no hay claves configuradas,
las funciones lanzan NoProviderError y quien llama usa el motor heurístico local.
"""
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class NoProviderError(RuntimeError):
    """No hay ningún proveedor de IA configurado."""


def resolve_provider() -> str | None:
    """Devuelve 'openai' | 'gemini' | None (motor heurístico local)."""
    provider = (settings.llm_provider or "auto").lower()
    if provider == "heuristic":
        return None
    if provider == "openai":
        return "openai" if settings.openai_api_key else None
    if provider == "gemini":
        return "gemini" if settings.gemini_api_key else None
    # auto: primera clave disponible
    if settings.openai_api_key:
        return "openai"
    if settings.gemini_api_key:
        return "gemini"
    return None


async def complete(system: str, prompt: str, temperature: float = 0.4) -> str:
    """Genera texto con el proveedor activo. Lanza NoProviderError si no hay ninguno."""
    provider = resolve_provider()
    if provider == "gemini":
        return await _gemini(system, prompt, temperature)
    if provider == "openai":
        return await _openai(system, prompt, temperature)
    raise NoProviderError("Sin proveedor de IA configurado")


async def _openai(system: str, prompt: str, temperature: float) -> str:
    url = settings.openai_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, json=payload, headers=headers)
    if res.status_code >= 400:
        raise RuntimeError(f"Proveedor OpenAI-compatible {res.status_code}: {res.text[:200]}")
    data = res.json()
    content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    if not content.strip():
        raise RuntimeError("El proveedor devolvió una respuesta vacía")
    return content.strip()


async def _gemini(system: str, prompt: str, temperature: float) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    headers = {"x-goog-api-key": settings.gemini_api_key}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        res = await client.post(url, json=payload, headers=headers)
    if res.status_code >= 400:
        raise RuntimeError(f"Gemini {res.status_code}: {res.text[:200]}")
    data = res.json()
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Gemini devolvió una respuesta inesperada")
    if not content.strip():
        raise RuntimeError("Gemini devolvió una respuesta vacía")
    return content.strip()
