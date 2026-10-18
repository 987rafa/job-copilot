"""Datos demo ficticios (sin información real) + resentado.

El perfil y las postulaciones de ejemplo permiten probar toda la app sin
configurar nada. Se cargan con SEED_ON_STARTUP=true o con POST /api/demo/reset.
"""
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.application import Application
from app.models.draft import Draft
from app.models.profile import Profile


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


DEMO_PROFILE = {
    "full_name": "Camila Restrepo",
    "headline": "Desarrolladora Full Stack — React + Python",
    "email": "camila.restrepo@example.com",
    "phone": "+57 300 555 0199",
    "location": "Medellín, Colombia · Remota",
    "links": "github.com/camilarestrepo · linkedin.com/in/camilarestrepo",
    "summary": (
        "Desarrolladora full stack con 3+ años de experiencia creando aplicaciones web: "
        "interfaces en React/TypeScript y APIs en Python (FastAPI) sobre PostgreSQL. "
        "Me gustan los productos bien pulidos, con tests y despliegue continuo."
    ),
    "skills": (
        "React, TypeScript, Python, FastAPI, SQLAlchemy, PostgreSQL, Docker, Git, pytest, "
        "REST APIs, Tailwind"
    ),
    "cv_text": (
        "Camila Restrepo — Desarrolladora Full Stack\n"
        "Medellín, Colombia · camila.restrepo@example.com · +57 300 555 0199\n\n"
        "EXPERIENCIA\n"
        "- Desarrolladora Full Stack, Kintsugi Apps (2023-2026): aplicaciones de gestión con "
        "React + TypeScript, APIs en FastAPI, PostgreSQL y Docker; CI/CD con GitHub Actions.\n"
        "- Practicante de desarrollo, Faro Labs (2022-2023): reportes automatizados en Python y "
        "dashboards internos en React.\n\n"
        "EDUCACIÓN\n"
        "- Ingeniería de Sistemas, Universidad de Antioquia (2022).\n\n"
        "SKILLS\n"
        "React, TypeScript, Python, FastAPI, SQLAlchemy, PostgreSQL, Docker, Git, pytest, "
        "REST APIs, Tailwind, inglés B2."
    ),
}


def _analysis(score: int, summary: str, strengths: list[str], gaps: list[str], kws: list[str]) -> dict:
    return {
        "fit_score": score,
        "summary": summary,
        "strengths": strengths,
        "gaps": gaps,
        "keywords": kws,
    }


_TODAY = date.today

DEMO_APPLICATIONS = [
    {
        "company": "Nuvora Labs",
        "role": "Full Stack Developer (React + Python)",
        "source": "LinkedIn",
        "url": "https://example.com/jobs/nuvora-fullstack",
        "status": "entrevista",
        "fit_score": 88,
        "job_text": (
            "Buscamos Full Stack con React, TypeScript, Python y FastAPI para construir APIs REST "
            "sobre PostgreSQL. Valoramos Docker, tests automatizados y microservicios. Inglés intermedio."
        ),
        "analysis": _analysis(
            88,
            "Encaje alto: el stack principal de la oferta (React + TypeScript + FastAPI) es "
            "exactamente el que usas a diario. La entrevista técnica debería ir bien.",
            ["React + TypeScript en producción", "APIs con FastAPI y PostgreSQL",
             "Docker y tests automatizados", "Inglés intermedio suficiente"],
            ["Experiencia formal en microservicios", "Kubernetes (deseable)"],
            ["react", "typescript", "python", "fastapi", "postgresql", "docker", "tests",
             "microservicios", "ingles"],
        ),
        "notes": "Primera entrevista agendada. Repasar diseño de microservicios y colas.",
        "next_followup": _TODAY() + timedelta(days=2),
        "applied_days_ago": 5,
        "created_days_ago": 12,
        "updated_days_ago": 1,
    },
    {
        "company": "Andes Commerce",
        "role": "Frontend Engineer (React)",
        "source": "LinkedIn",
        "url": "https://example.com/jobs/andes-react",
        "status": "aplicada",
        "fit_score": 84,
        "job_text": (
            "Frontend Engineer para e-commerce con React, TypeScript y Tailwind. Consumo de APIs "
            "REST, componentes accesibles y experiencia de usuario. Next.js deseable."
        ),
        "analysis": _analysis(
            84,
            "Muy buen encaje en frontend: React + TypeScript con Tailwind es tu base. Lo único "
            "pendiente es Next.js, que aparece como deseable.",
            ["React + TypeScript", "UI con Tailwind", "Consumo de APIs REST"],
            ["Next.js (deseable)", "Storybook (deseable)"],
            ["react", "typescript", "tailwind", "next.js", "api rest", "e-commerce"],
        ),
        "notes": "Enviada con carta personalizada. Hacer seguimiento si no responden en 5 días.",
        "next_followup": _TODAY() + timedelta(days=5),
        "applied_days_ago": 2,
        "created_days_ago": 6,
        "updated_days_ago": 2,
    },
    {
        "company": "Fintegra",
        "role": "Backend Python Developer",
        "source": "Computrabajo",
        "url": "https://example.com/jobs/fintegra-python",
        "status": "aplicada",
        "fit_score": 79,
        "job_text": (
            "Desarrollador Backend con Python, FastAPI, SQLAlchemy y PostgreSQL para productos "
            "fintech. Docker y CI/CD en el día a día. AWS deseable."
        ),
        "analysis": _analysis(
            79,
            "Buen encaje backend: Python, FastAPI y PostgreSQL están cubiertos. AWS y el "
            "conocimiento fintech son las brechas principales.",
            ["Python y FastAPI", "SQLAlchemy + PostgreSQL", "Docker y CI/CD"],
            ["Experiencia en fintech", "AWS (deseable)"],
            ["python", "fastapi", "sqlalchemy", "postgresql", "docker", "aws", "fintech", "ci/cd"],
        ),
        "notes": "Piden prueba técnica de API REST. Revisar requisitos de facturación electrónica.",
        "next_followup": None,
        "applied_days_ago": 4,
        "created_days_ago": 10,
        "updated_days_ago": 3,
    },
    {
        "company": "HealthLab Digital",
        "role": "Full Stack Web (React + FastAPI)",
        "source": "Torre",
        "url": "https://example.com/jobs/healthlab-fullstack",
        "status": "guardada",
        "fit_score": 74,
        "job_text": (
            "Full Stack para plataforma de salud: React, Python/FastAPI, PostgreSQL. Deseable "
            "experiencia con HL7/FHIR e inglés B2+ para reuniones con clientes en EE. UU."
        ),
        "analysis": _analysis(
            74,
            "Encaje razonable: el stack técnico coincide, pero el dominio salud y el inglés B2+ "
            "son puntos a preparar antes de postular.",
            ["React + FastAPI + PostgreSQL", "Tests automatizados"],
            ["HL7/FHIR (deseable)", "Inglés B2+ para clientes"],
            ["react", "fastapi", "postgresql", "salud", "hl7", "fhir", "ingles"],
        ),
        "notes": "No postulada aún. Investigar qué es FHIR y decidir si vale la pena.",
        "next_followup": None,
        "created_days_ago": 1,
        "updated_days_ago": 1,
    },
    {
        "company": "PixelWorks Studio",
        "role": "React Developer",
        "source": "Referido",
        "url": "https://example.com/jobs/pixelworks-react",
        "status": "entrevista",
        "fit_score": 81,
        "job_text": (
            "Estudio de producto busca React Developer con TypeScript, CSS moderno y Storybook. "
            "Trabajo cercano con diseño, animaciones y metodologías ágiles (Scrum)."
        ),
        "analysis": _analysis(
            81,
            "Buen encaje: React + TypeScript y el trabajo con diseño encajan contigo. Las "
            "animaciones avanzadas son la parte a reforzar.",
            ["React + TypeScript", "Colaboración con diseño", "Scrum"],
            ["Animaciones avanzadas (Framer Motion)", "Storybook en profundidad"],
            ["react", "typescript", "css", "storybook", "animaciones", "scrum"],
        ),
        "notes": "Segunda entrevista: prueba práctica de componente animado.",
        "next_followup": _TODAY() + timedelta(days=1),
        "applied_days_ago": 9,
        "created_days_ago": 16,
        "updated_days_ago": 2,
    },
    {
        "company": "CloudBridge",
        "role": "Python API Engineer",
        "source": "LinkedIn",
        "url": "https://example.com/jobs/cloudbridge-python",
        "status": "oferta",
        "fit_score": 90,
        "job_text": (
            "Python API Engineer para plataforma B2B: FastAPI, PostgreSQL, Docker, colas y "
            "observabilidad. Certificación AWS deseable. Equipo 100 % remoto."
        ),
        "analysis": _analysis(
            90,
            "Encaje excelente: el día a día de la vacante es tu stack actual. Solo la "
            "certificación AWS aparece como plus no obligatorio.",
            ["FastAPI + PostgreSQL", "Docker y despliegues", "APIs para producto B2B"],
            ["Certificación AWS (deseable)"],
            ["python", "fastapi", "postgresql", "docker", "colas", "aws", "remoto"],
        ),
        "notes": "OFERTA recibida. Negociar salario y fecha de inicio. Comparar con contraoferta.",
        "next_followup": None,
        "applied_days_ago": 15,
        "created_days_ago": 22,
        "updated_days_ago": 5,
    },
    {
        "company": "Mercado Andino",
        "role": "Desarrollador Full Stack Senior",
        "source": "Computrabajo",
        "url": "https://example.com/jobs/mercado-andino-senior",
        "status": "rechazada",
        "fit_score": 62,
        "job_text": (
            "Full Stack Senior con 6+ años, liderazgo de equipos, inglés avanzado y "
            "disponibilidad para viajar. Stack React + Node.js + PostgreSQL."
        ),
        "analysis": _analysis(
            62,
            "Encaje medio: el stack frontend coincide, pero piden perfil senior con liderazgo y "
            "experiencia que esta vacante no cubre. Sirve de práctica para feedback.",
            ["React + PostgreSQL", "Trabajo remoto con equipos"],
            ["6+ años y liderazgo de equipo", "Inglés avanzado", "Disponibilidad para viajar"],
            ["react", "node.js", "postgresql", "liderazgo", "ingles avanzado", "senior"],
        ),
        "notes": "Rechazada: pedían perfil senior con liderazgo. Guardar feedback para futuras.",
        "next_followup": None,
        "applied_days_ago": 21,
        "created_days_ago": 30,
        "updated_days_ago": 20,
    },
    {
        "company": "Aurora Fintech",
        "role": "Full Stack Developer",
        "source": "LinkedIn",
        "url": "https://example.com/jobs/aurora-fullstack",
        "status": "guardada",
        "fit_score": 71,
        "job_text": (
            "Full Stack con React y Python para banca digital. Kubernetes, inglés C1 y "
            "experiencia senior en equipos distribuidos."
        ),
        "analysis": _analysis(
            71,
            "Encaje medio-alto: el stack coincide, pero Kubernetes e inglés C1 quedan lejos del "
            "perfil actual. Postular solo si se refuerzan esas brechas.",
            ["React y Python", "APIs financieras"],
            ["Kubernetes", "Inglés C1", "Experiencia senior"],
            ["react", "python", "kubernetes", "ingles c1", "banca", "senior"],
        ),
        "notes": "Evaluar: quizá sea demasiado senior. Buscar su equivalente junior/medio.",
        "next_followup": None,
        "created_days_ago": 0,
        "updated_days_ago": 0,
    },
]

DEMO_DRAFTS = [
    {
        "application_index": 0,
        "kind": "carta",
        "language": "es",
        "tone": "profesional",
        "content": (
            "Estimado equipo de Nuvora Labs:\n\n"
            "Me postulo al puesto de Full Stack Developer (React + Python). Soy desarrolladora "
            "full stack con 3+ años de experiencia construyendo aplicaciones web con React, "
            "TypeScript, Python y FastAPI sobre PostgreSQL; trabajo a diario con Docker, tests "
            "automatizados y despliegue continuo.\n\n"
            "En mi rol actual lidero el desarrollo de una plataforma de gestión usada por más de "
            "200 equipos: diseñé sus APIs en FastAPI, migré el frontend a TypeScript y reduje los "
            "tiempos de despliegue con CI/CD. Creo que ese recorrido encaja con el perfil que "
            "buscan, incluida la parte de microservicios y colas.\n\n"
            "Me encantaría conversar sobre cómo puedo aportar al equipo. Gracias por su tiempo.\n\n"
            "Saludos cordiales,\nCamila Restrepo\n"
            "camila.restrepo@example.com · +57 300 555 0199 · Medellín, Colombia"
        ),
    },
    {
        "application_index": 1,
        "kind": "mensaje",
        "language": "es",
        "tone": "cercano",
        "content": (
            "Hola, equipo de Andes Commerce: vi la vacante de Frontend Engineer (React) y quería "
            "escribirles. Trabajo a diario con React, TypeScript y Tailwind sobre APIs REST, y me "
            "encantaría aportar en su e-commerce. ¿Les parece si conversamos? ¡Gracias!"
        ),
    },
    {
        "application_index": 5,
        "kind": "carta",
        "language": "en",
        "tone": "entusiasta",
        "content": (
            "Dear CloudBridge team:\n\n"
            "I am thrilled to apply for the Python API Engineer position. I build production APIs "
            "with Python, FastAPI and PostgreSQL, and I ship them with Docker, automated tests and "
            "CI/CD pipelines.\n\n"
            "At my current job I own the backend of a B2B platform: I designed its public API, "
            "added observability and cut response times by 40 %. A fully remote team with a "
            "product focus is exactly where I want to grow next.\n\n"
            "I would love to discuss how I can contribute. Thank you for your time.\n\n"
            "Best regards,\nCamila Restrepo\n"
            "camila.restrepo@example.com · +57 300 555 0199 · Medellín, Colombia"
        ),
    },
]


def _build_application(item: dict) -> Application:
    now = _now()
    created_days = item.get("created_days_ago", 10)
    updated_days = item.get("updated_days_ago", created_days)
    applied_days = item.get("applied_days_ago")
    return Application(
        company=item["company"],
        role=item["role"],
        source=item.get("source", ""),
        url=item.get("url", ""),
        job_text=item.get("job_text", ""),
        status=item["status"],
        fit_score=item.get("fit_score"),
        analysis=item.get("analysis"),
        notes=item.get("notes", ""),
        next_followup=item.get("next_followup"),
        applied_at=now - timedelta(days=applied_days) if applied_days is not None else None,
        created_at=now - timedelta(days=created_days),
        updated_at=now - timedelta(days=updated_days),
    )


def reset_demo_data(db: Session) -> dict:
    """Borra postulaciones/borradores y vuelve a sembrar el perfil y los ejemplos."""
    db.query(Draft).delete()
    db.query(Application).delete()

    profile = db.query(Profile).first()
    if profile is None:
        profile = Profile()
        db.add(profile)
    for field, value in DEMO_PROFILE.items():
        setattr(profile, field, value)

    applications = [_build_application(item) for item in DEMO_APPLICATIONS]
    db.add_all(applications)
    db.flush()

    drafts = [
        Draft(
            application_id=applications[item["application_index"]].id,
            kind=item["kind"],
            language=item["language"],
            tone=item["tone"],
            content=item["content"],
        )
        for item in DEMO_DRAFTS
    ]
    db.add_all(drafts)
    db.commit()
    return {"applications": len(applications), "drafts": len(drafts)}


def run_seed() -> None:
    """Siembra al arrancar solo si no hay postulaciones todavía."""
    with SessionLocal() as db:
        if db.query(Application).first() is None:
            reset_demo_data(db)
