"""Dependencias compartidas de la API."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.profile import Profile


def get_profile(db: Session = Depends(get_db)) -> Profile:
    """Perfil singleton: se crea vacío la primera vez que se pide."""
    profile = db.query(Profile).first()
    if profile is None:
        profile = Profile()
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
