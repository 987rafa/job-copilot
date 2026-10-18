"""Panel: métricas del tablero de postulaciones."""
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import APPLICATION_STATUSES, Application
from app.schemas.application import ApplicationRead
from app.schemas.dashboard import DashboardRead
from app.services.llm import resolve_provider

router = APIRouter(prefix="/dashboard", tags=["panel"])


@router.get("", response_model=DashboardRead)
def dashboard(db: Session = Depends(get_db)):
    by_status = {status: 0 for status in APPLICATION_STATUSES}
    for status, count in (
        db.query(Application.status, func.count(Application.id)).group_by(Application.status).all()
    ):
        if status in by_status:
            by_status[status] = count
    total = sum(by_status.values())
    active = by_status["guardada"] + by_status["aplicada"] + by_status["entrevista"]

    avg_fit = (
        db.query(func.avg(Application.fit_score))
        .filter(Application.fit_score.isnot(None))
        .scalar()
    )

    week_ago = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=7)
    applied_this_week = (
        db.query(func.count(Application.id))
        .filter(Application.applied_at.isnot(None), Application.applied_at >= week_ago)
        .scalar()
        or 0
    )

    upcoming = (
        db.query(Application)
        .filter(
            Application.next_followup.isnot(None),
            Application.next_followup <= date.today() + timedelta(days=7),
        )
        .order_by(Application.next_followup.asc())
        .limit(10)
        .all()
    )
    recent = (
        db.query(Application)
        .order_by(Application.updated_at.desc(), Application.id.desc())
        .limit(6)
        .all()
    )

    return DashboardRead(
        total=total,
        active=active,
        by_status=by_status,
        avg_fit=float(avg_fit) if avg_fit is not None else None,
        applied_this_week=int(applied_this_week),
        upcoming_followups=[ApplicationRead.model_validate(x) for x in upcoming],
        recent=[ApplicationRead.model_validate(x) for x in recent],
        llm=resolve_provider() or "heuristic",
    )
