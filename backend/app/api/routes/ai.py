"""Funciones de IA: análisis de ofertas y borradores."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_profile
from app.db.session import get_db
from app.models.application import Application
from app.models.draft import Draft
from app.models.profile import Profile
from app.schemas.ai import AnalyzeRequest, AnalyzeResponse, DraftRead, DraftRequest
from app.services import analysis

router = APIRouter(prefix="/ai", tags=["IA"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_job(
    data: AnalyzeRequest,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_profile),
):
    """Compara una oferta con el perfil. Con `save=true` además la guarda en el tablero."""
    result = await analysis.analyze(profile, data.job_text)
    application_id = None
    if data.save:
        if not (data.company.strip() and data.role.strip()):
            raise HTTPException(422, "Para guardar la postulación envía empresa y cargo")
        application = Application(
            company=data.company.strip(),
            role=data.role.strip(),
            source=data.source.strip(),
            url=data.url.strip(),
            job_text=data.job_text,
            analysis=result,
            fit_score=result["fit_score"],
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        application_id = application.id
    return AnalyzeResponse(analysis=result, application_id=application_id)


@router.post("/drafts", response_model=DraftRead, status_code=201)
async def create_draft(
    data: DraftRequest,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_profile),
):
    """Genera una carta/mensaje/seguimiento y lo guarda en el historial."""
    application = None
    if data.application_id is not None:
        application = db.get(Application, data.application_id)
        if application is None:
            raise HTTPException(404, "Postulación no encontrada")

    content = await analysis.generate_draft(
        profile,
        job_text=data.job_text or (application.job_text if application else ""),
        company=application.company if application else "",
        role=application.role if application else "",
        kind=data.kind,
        language=data.language,
        tone=data.tone,
        extra_notes=data.extra_notes,
    )
    draft = Draft(
        application_id=data.application_id,
        kind=data.kind,
        language=data.language,
        tone=data.tone,
        content=content,
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


@router.get("/drafts", response_model=list[DraftRead])
def list_drafts(
    application_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Draft)
    if application_id is not None:
        query = query.filter(Draft.application_id == application_id)
    return query.order_by(Draft.created_at.desc(), Draft.id.desc()).limit(limit).all()
