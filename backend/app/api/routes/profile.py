"""Perfil del usuario: datos y CV (subida de PDF/txt)."""
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_profile
from app.db.session import get_db
from app.models.profile import Profile
from app.schemas.profile import CvUploadResult, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["perfil"])

MAX_CV_BYTES = 5 * 1024 * 1024


@router.get("", response_model=ProfileRead)
def read_profile(profile: Profile = Depends(get_profile)):
    return profile


@router.put("", response_model=ProfileRead)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_profile),
):
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(profile, field, value)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/cv", response_model=CvUploadResult)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    profile: Profile = Depends(get_profile),
):
    """Extrae el texto del CV (PDF, .txt o .md) y lo guarda en el perfil."""
    raw = await file.read()
    if len(raw) > MAX_CV_BYTES:
        raise HTTPException(413, "El archivo supera el límite de 5 MB")

    filename = (file.filename or "").lower()
    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(raw))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        except Exception as exc:
            raise HTTPException(400, f"No se pudo leer el PDF: {exc}") from exc
    elif filename.endswith((".txt", ".md")):
        text = raw.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(400, "Formato no soportado: sube un PDF, .txt o .md")

    text = text.strip()
    if not text:
        raise HTTPException(422, "No se extrajo texto del archivo")

    profile.cv_text = text
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return CvUploadResult(
        filename=file.filename or "cv",
        chars=len(text),
        profile=ProfileRead.model_validate(profile),
    )
