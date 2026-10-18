"""Postulaciones: CRUD + filtros."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import Application
from app.models.draft import Draft
from app.schemas.application import (
    ApplicationCreate,
    ApplicationList,
    ApplicationRead,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["postulaciones"])

# Estados en los que la postulación ya salió del tablero de "pendientes"
APPLIED_STATUSES = ("aplicada", "entrevista", "oferta")


def _get_or_404(db: Session, application_id: int) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(404, "Postulación no encontrada")
    return application


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("", response_model=ApplicationList)
def list_applications(
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(Application.company.ilike(pattern), Application.role.ilike(pattern))
        )
    total = query.count()
    items = (
        query.order_by(Application.updated_at.desc(), Application.id.desc()).limit(limit).all()
    )
    return ApplicationList(items=[ApplicationRead.model_validate(i) for i in items], total=total)


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    application = Application(**data.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, application_id)


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)
):
    application = _get_or_404(db, application_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(application, field, value)
    new_status = changes.get("status")
    if new_status in APPLIED_STATUSES and application.applied_at is None:
        application.applied_at = _utcnow()
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    application = _get_or_404(db, application_id)
    # Los borradores quedan huérfanos sin romper la FK (útil para reutilizarlos)
    db.query(Draft).filter(Draft.application_id == application_id).update(
        {"application_id": None}
    )
    db.delete(application)
    db.commit()
