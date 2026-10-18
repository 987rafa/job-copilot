"""Configuración central (pydantic-settings) — se lee de variables de entorno o .env."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Job Copilot"
    version: str = "0.1.0"

    database_url: str = "sqlite:///./job-copilot.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    seed_on_startup: bool = False

    # ── IA ──────────────────────────────────────────────────────
    # auto = usa la primera clave disponible (OpenAI-compatible > Gemini > heurístico local)
    llm_provider: str = "auto"  # auto | openai | gemini | heuristic
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
