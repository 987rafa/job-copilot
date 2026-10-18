"""Demo: reiniciar los datos de ejemplo."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.seed import reset_demo_data

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/reset")
def reset_demo(db: Session = Depends(get_db)):
    counts = reset_demo_data(db)
    return {"ok": True, **counts}
