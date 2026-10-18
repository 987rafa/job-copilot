"""Análisis de ofertas y redacción de borradores.

Si hay un proveedor de IA configurado (cualquier API compatible con OpenAI o
Gemini) se usa el LLM. Si no hay claves —o si el proveedor falla—, un motor
heurístico local (coincidencia de palabras clave + plantillas) mantiene la app
100 % funcional: ideal para demos, tests y uso sin conexión.
"""
import json
import logging
import re
import unicodedata
from collections import Counter

from app.models.profile import Profile
from app.services import llm

logger = logging.getLogger(__name__)

WORD_RE = re.compile(r"[a-z0-9+#.]+")

STOPWORDS: set[str] = set(
    """
    a al algo algunos ante antes como con contra cual cuando de del desde donde dos el ella ellas
    ello ellos en entre era erais eran eras eres es esa esas ese eso esos esta estaba estado estas
    este esto estos fue fueron ha han hasta hay la las le les lo los mas me mi mis mucho muchos muy
    no nos nosotros o os otra otras otro otros para pero poco por porque que quien quienes se sea
    segun ser si sin sobre solo son su sus te tiene tienen todo todos tu tus un una unas uno unos y ya
    anos experiencia trabajo empresa equipo puesto cargo rol buscamos buscando requerimos oferta
    vacante candidato candidata ideal deseable requisitos responsabilidades funciones
    the a an and or of to in for on with at by from as is are was were be been being it its this
    that these those you your we our they their he she his her i me my not do does did have has had
    will would can could should
    """.split()
)

SYSTEM_ANALYST = (
    "Eres un analista de selección con años de experiencia evaluando candidaturas. "
    "Comparas ofertas de trabajo con perfiles profesionales y respondes SIEMPRE con JSON válido, "
    "sin texto adicional ni bloques de código."
)

SYSTEM_WRITER = (
    "Eres un redactor profesional de postulaciones. Escribes en el idioma que se te pida, con tono "
    "humano y natural. Nunca inventas experiencia que no aparezca en el perfil ni usas marcadores "
    "como [empresa] o [puesto]; si falta un dato, lo omites con elegancia. "
    "Respondes únicamente con el texto final, listo para enviar."
)


# ── Utilidades de texto ───────────────────────────────────────────

def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def keywords(text: str, limit: int = 25) -> list[tuple[str, int]]:
    """Palabras clave más frecuentes (sin tildes, sin stopwords)."""
    tokens = WORD_RE.findall(_normalize(text))
    counter = Counter(t for t in tokens if len(t) >= 3 and not t.isdigit() and t not in STOPWORDS)
    return counter.most_common(limit)


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw.strip())
    start, end = raw.find("{"), raw.rfind("}")
    if start != -1 and end != -1:
        raw = raw[start : end + 1]
    return json.loads(raw)


# ── Análisis ──────────────────────────────────────────────────────

def heuristic_analysis(profile: Profile, job_text: str) -> dict:
    """Motor local: coincidencia de palabras clave entre CV/perfil y oferta."""
    cv_text = " ".join([profile.headline, profile.summary, profile.skills, profile.cv_text])
    cv_kw = {k for k, _ in keywords(cv_text, limit=500)}
    job_kw = keywords(job_text, limit=18)

    matched = [k for k, _ in job_kw if k in cv_kw]
    missing = [k for k, _ in job_kw if k not in cv_kw]
    total = len(job_kw)
    score = round(100 * len(matched) / total) if total else 50
    score = max(5, min(97, score))

    if matched:
        summary = (
            f"Análisis local (sin clave de IA): {len(matched)} de {total} palabras clave de la "
            f"oferta aparecen en tu perfil. Destacan: {', '.join(matched[:4])}."
        )
    else:
        summary = (
            "Análisis local (sin clave de IA): casi ninguna palabra clave de la oferta aparece en "
            "tu perfil. Refuerza tu CV con los términos de «A reforzar» o configura una clave de IA."
        )

    return {
        "fit_score": score,
        "summary": summary,
        "strengths": matched[:8],
        "gaps": missing[:8],
        "keywords": [k for k, _ in job_kw],
    }


def _profile_block(profile: Profile) -> str:
    parts = [
        f"Nombre: {profile.full_name or '(sin nombre)'}",
        f"Titular: {profile.headline}" if profile.headline else "",
        f"Ubicación: {profile.location}" if profile.location else "",
        f"Resumen: {profile.summary}" if profile.summary else "",
        f"Habilidades: {profile.skills}" if profile.skills else "",
        f"CV:\n{profile.cv_text[:3000]}" if profile.cv_text else "",
    ]
    return "\n".join(p for p in parts if p)


def _analysis_prompt(profile: Profile, job_text: str) -> str:
    return (
        "Compara esta oferta de trabajo con el perfil del candidato.\n\n"
        f"## Perfil\n{_profile_block(profile)}\n\n"
        f"## Oferta\n{job_text[:6000]}\n\n"
        "Devuelve SOLO este JSON (en español):\n"
        "{\n"
        '  "fit_score": <0-100, qué tan bien encaja el perfil>,\n'
        '  "summary": "<2-3 frases de veredicto>",\n'
        '  "strengths": ["<punto donde el perfil encaja>", "...máx 6"],\n'
        '  "gaps": ["<requisito que falta o conviene reforzar>", "...máx 6"],\n'
        '  "keywords": ["<palabra clave de la oferta>", "...máx 12"]\n'
        "}"
    )


async def analyze(profile: Profile, job_text: str) -> dict:
    """Analiza una oferta contra el perfil (LLM si hay clave; heurístico si no)."""
    try:
        raw = await llm.complete(SYSTEM_ANALYST, _analysis_prompt(profile, job_text), temperature=0.2)
        data = _parse_json(raw)
        return {
            "fit_score": int(max(0, min(100, data.get("fit_score", 50)))),
            "summary": str(data.get("summary", "")).strip(),
            "strengths": [str(x) for x in (data.get("strengths") or [])][:6],
            "gaps": [str(x) for x in (data.get("gaps") or [])][:6],
            "keywords": [str(x) for x in (data.get("keywords") or [])][:12],
        }
    except llm.NoProviderError:
        return heuristic_analysis(profile, job_text)
    except Exception as exc:  # red inválida, respuesta no-JSON, límite de cuota…
        logger.warning("IA falló (%s); uso el análisis heurístico", exc)
        return heuristic_analysis(profile, job_text)


# ── Borradores (carta / mensaje / seguimiento) ────────────────────

def heuristic_draft(
    profile: Profile,
    *,
    company: str = "",
    role: str = "",
    kind: str = "carta",
    language: str = "es",
    tone: str = "profesional",
    extra_notes: str = "",
) -> str:
    """Plantilla local para generar borradores sin IA."""
    name = profile.full_name or ("Your name" if language == "en" else "Tu nombre")
    skills = ", ".join(s.strip() for s in (profile.skills or "").split(",") if s.strip())[:200]
    contact = " · ".join(x for x in (profile.email, profile.phone, profile.location) if x)

    if language == "en":
        target = f"the {role} position" if role else "the open position"
        if kind == "carta":
            lines = [f"Dear {company} team:" if company else "Dear hiring team:", ""]
            lines.append(
                f"I am writing to apply for {target}. "
                + (f"{profile.headline}. " if profile.headline else "")
                + (f"I work daily with {skills}. " if skills else "")
                + "I believe my experience matches what the role requires."
            )
            if profile.summary:
                lines += ["", profile.summary]
            if extra_notes:
                lines += ["", f"One more thing: {extra_notes}"]
            lines += ["", "I would love to talk about how I can contribute. Thank you for your time.", "", "Best regards,", name]
            if contact:
                lines.append(contact)
            return "\n".join(lines)
        if kind == "mensaje":
            base = f"Hi {company} team! I saw {target} and wanted to reach out."
            if skills:
                base += f" I build web apps with {skills}."
            if extra_notes:
                base += f" {extra_notes}"
            return base + " Would you be open to a quick chat? Thanks!"
        return (
            f"Hi {company or 'there'}, I applied for {target} a few days ago and wanted to follow up "
            f"briefly. I'm still very interested. Thanks for your time!\n\n{name}"
        )

    # ── español ──
    target = role or "la vacante"
    if kind == "carta":
        lines = [f"Estimado equipo de {company}:" if company else "Estimado equipo:", ""]
        lines.append(
            f"Me postulo a {target}. "
            + (f"{profile.headline}. " if profile.headline else "")
            + (f"Trabajo a diario con {skills}. " if skills else "")
            + "Creo que mi experiencia encaja con lo que busca la posición."
        )
        if profile.summary:
            lines += ["", profile.summary]
        if extra_notes:
            lines += ["", f"Quisiera añadir: {extra_notes}"]
        lines += ["", "Me encantaría conversar sobre cómo puedo aportar al equipo. Gracias por su tiempo.", "", "Saludos cordiales,", name]
        if contact:
            lines.append(contact)
        return "\n".join(lines)
    if kind == "mensaje":
        greeting = f"Hola, equipo de {company}:" if company else "Hola:"
        base = f"{greeting} vi {target} y quería escribirles."
        if skills:
            base += f" Construyo aplicaciones web con {skills}."
        if extra_notes:
            base += f" {extra_notes}"
        return base + " ¿Les parece si conversamos? ¡Gracias!"
    greeting = f"Hola, equipo de {company}:" if company else "Hola:"
    return (
        f"{greeting} hace unos días envié mi postulación para {target} y quería hacer un "
        f"seguimiento breve. Sigo muy interesado/a en la oportunidad. ¡Gracias por su tiempo!\n\n{name}"
    )


def _draft_prompt(
    profile: Profile,
    *,
    job_text: str,
    company: str,
    role: str,
    kind: str,
    language: str,
    tone: str,
    extra_notes: str,
) -> str:
    kind_desc = {
        "carta": "una carta de presentación (3-4 párrafos: saludo, por qué encajas, cierre)",
        "mensaje": "un mensaje corto (máximo 4 frases) para LinkedIn o WhatsApp",
        "seguimiento": "un mensaje breve de seguimiento tras haber aplicado",
    }[kind]
    idioma = "español" if language == "es" else "inglés"
    context = []
    if company:
        context.append(f"Empresa: {company}")
    if role:
        context.append(f"Puesto: {role}")
    if job_text:
        context.append(f"Oferta (extracto):\n{job_text[:3000]}")
    if extra_notes:
        context.append(f"Notas del candidato a mencionar: {extra_notes}")
    context_block = ("\n\n## Contexto\n" + "\n".join(context)) if context else ""
    return (
        f"Escribe {kind_desc} en {idioma}, con tono {tone}.\n\n"
        f"## Perfil del candidato\n{_profile_block(profile)}"
        f"{context_block}\n\n"
        "Devuelve solo el texto final, listo para enviar."
    )


async def generate_draft(
    profile: Profile,
    *,
    job_text: str = "",
    company: str = "",
    role: str = "",
    kind: str = "carta",
    language: str = "es",
    tone: str = "profesional",
    extra_notes: str = "",
) -> str:
    """Genera una carta/mensaje/seguimiento (LLM si hay clave; plantilla si no)."""
    try:
        raw = await llm.complete(
            SYSTEM_WRITER,
            _draft_prompt(
                profile,
                job_text=job_text,
                company=company,
                role=role,
                kind=kind,
                language=language,
                tone=tone,
                extra_notes=extra_notes,
            ),
            temperature=0.7,
        )
        if raw.strip():
            return raw.strip()
        raise RuntimeError("respuesta vacía")
    except llm.NoProviderError:
        return heuristic_draft(
            profile, company=company, role=role, kind=kind,
            language=language, tone=tone, extra_notes=extra_notes,
        )
    except Exception as exc:
        logger.warning("IA falló al redactar (%s); uso la plantilla local", exc)
        return heuristic_draft(
            profile, company=company, role=role, kind=kind,
            language=language, tone=tone, extra_notes=extra_notes,
        )
