from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401 — importa los modelos para registrarlos en Base.metadata
from app.api.routes import ai, applications, dashboard, demo, profile
from app.api.routes import health as health_routes
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.services.llm import resolve_provider


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_on_startup:
        from app.seed import run_seed

        run_seed()
    yield


app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(health_routes.router)
api.include_router(profile.router)
api.include_router(applications.router)
api.include_router(ai.router)
api.include_router(dashboard.router)
api.include_router(demo.router)
app.include_router(api)

# Alias sin prefijo para health checks de plataformas (Render, Docker, etc.)
app.include_router(health_routes.router)


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "llm": resolve_provider() or "heuristic",
    }
