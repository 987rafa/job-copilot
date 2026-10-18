def _create(client, **overrides):
    payload = {
        "company": "Acme",
        "role": "Backend Developer",
        "source": "LinkedIn",
        "job_text": "Python FastAPI PostgreSQL",
    }
    payload.update(overrides)
    res = client.post("/api/applications", json=payload)
    assert res.status_code == 201
    return res.json()


def test_create_and_get(client):
    created = _create(client, company="Acme Corp")
    assert created["status"] == "guardada"
    assert created["fit_score"] is None

    res = client.get(f"/api/applications/{created['id']}")
    assert res.status_code == 200
    assert res.json()["company"] == "Acme Corp"


def test_create_requires_company_and_role(client):
    res = client.post("/api/applications", json={"company": "", "role": "Dev"})
    assert res.status_code == 422


def test_list_and_filter_by_status(client):
    first = _create(client, company="Uno")
    _create(client, company="Dos")

    res = client.get("/api/applications")
    assert res.status_code == 200
    assert res.json()["total"] == 2

    res = client.patch(f"/api/applications/{first['id']}", json={"status": "aplicada"})
    assert res.status_code == 200

    res = client.get("/api/applications", params={"status": "aplicada"})
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["company"] == "Uno"


def test_search_by_query(client):
    _create(client, company="Globant Colombia")
    _create(client, company="Otro")

    res = client.get("/api/applications", params={"q": "globant"})
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["company"] == "Globant Colombia"


def test_patch_status_sets_applied_at(client):
    created = _create(client)
    assert created["applied_at"] is None

    res = client.patch(f"/api/applications/{created['id']}", json={"status": "aplicada"})
    assert res.status_code == 200
    assert res.json()["applied_at"] is not None


def test_patch_notes_and_followup(client):
    created = _create(client)
    res = client.patch(
        f"/api/applications/{created['id']}",
        json={"notes": "Enviar portafolio", "next_followup": "2026-11-02"},
    )
    assert res.status_code == 200
    assert res.json()["notes"] == "Enviar portafolio"
    assert res.json()["next_followup"] == "2026-11-02"


def test_patch_invalid_status(client):
    created = _create(client)
    res = client.patch(f"/api/applications/{created['id']}", json={"status": "en_proceso"})
    assert res.status_code == 422


def test_delete_application(client):
    created = _create(client)
    res = client.delete(f"/api/applications/{created['id']}")
    assert res.status_code == 204
    assert client.get(f"/api/applications/{created['id']}").status_code == 404


def test_missing_application_404(client):
    assert client.get("/api/applications/999").status_code == 404
    assert client.patch("/api/applications/999", json={"notes": "x"}).status_code == 404
