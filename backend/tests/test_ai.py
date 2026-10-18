JOB = (
    "Buscamos desarrollador con Python, FastAPI, SQL y Docker para construir APIs REST. "
    "React y TypeScript deseables."
)


def _full_profile(client):
    res = client.put(
        "/api/profile",
        json={
            "full_name": "Ana Pérez",
            "headline": "Full Stack Developer",
            "skills": "Python, React, FastAPI, SQL, Docker, TypeScript",
            "summary": "Desarrolladora full stack enfocada en APIs y productos web.",
        },
    )
    assert res.status_code == 200


def test_analyze_heuristic(client):
    _full_profile(client)
    res = client.post("/api/ai/analyze", json={"job_text": JOB})
    assert res.status_code == 200
    analysis = res.json()["analysis"]
    assert res.json()["application_id"] is None
    assert 0 <= analysis["fit_score"] <= 100
    assert analysis["keywords"]
    assert analysis["summary"]
    lowered = [k.lower() for k in analysis["keywords"]]
    assert "python" in lowered
    assert "fastapi" in lowered
    # El perfil cubre varias palabras clave → puntaje razonable
    assert analysis["fit_score"] >= 40


def test_analyze_too_short(client):
    res = client.post("/api/ai/analyze", json={"job_text": "muy corta"})
    assert res.status_code == 422


def test_analyze_save_requires_company_and_role(client):
    res = client.post("/api/ai/analyze", json={"job_text": JOB, "save": True})
    assert res.status_code == 422


def test_analyze_save_creates_application(client):
    _full_profile(client)
    res = client.post(
        "/api/ai/analyze",
        json={"job_text": JOB, "save": True, "company": "Acme", "role": "Backend Dev"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["application_id"] is not None

    saved = client.get(f"/api/applications/{body['application_id']}").json()
    assert saved["company"] == "Acme"
    assert saved["fit_score"] == body["analysis"]["fit_score"]
    assert saved["analysis"]["fit_score"] == body["analysis"]["fit_score"]
    assert saved["status"] == "guardada"


def test_draft_carta_es(client):
    _full_profile(client)
    res = client.post(
        "/api/ai/drafts",
        json={"job_text": JOB, "kind": "carta", "language": "es", "tone": "profesional"},
    )
    assert res.status_code == 201
    draft = res.json()
    assert "Ana Pérez" in draft["content"]
    assert draft["kind"] == "carta"

    listing = client.get("/api/ai/drafts").json()
    assert len(listing) == 1
    assert listing[0]["id"] == draft["id"]


def test_draft_for_saved_application(client):
    _full_profile(client)
    created = client.post(
        "/api/applications",
        json={"company": "Acme Corp", "role": "Backend Developer", "job_text": JOB},
    ).json()

    res = client.post("/api/ai/drafts", json={"application_id": created["id"], "kind": "carta"})
    assert res.status_code == 201
    body = res.json()
    assert "Acme Corp" in body["content"]
    assert body["application_id"] == created["id"]


def test_draft_requires_source(client):
    res = client.post("/api/ai/drafts", json={})
    assert res.status_code == 422


def test_draft_english(client):
    _full_profile(client)
    res = client.post(
        "/api/ai/drafts",
        json={"job_text": JOB, "kind": "carta", "language": "en"},
    )
    assert res.status_code == 201
    assert res.json()["content"].startswith("Dear")


def test_draft_seguimiento(client):
    _full_profile(client)
    res = client.post(
        "/api/ai/drafts",
        json={"job_text": JOB, "kind": "seguimiento", "language": "es"},
    )
    assert res.status_code == 201
    assert "seguimiento" in res.json()["content"].lower()


def test_draft_unknown_application_404(client):
    res = client.post("/api/ai/drafts", json={"application_id": 999})
    assert res.status_code == 404
