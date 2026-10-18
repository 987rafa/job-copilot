def test_get_profile_creates_default(client):
    res = client.get("/api/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["full_name"] == ""


def test_update_profile(client):
    res = client.put(
        "/api/profile",
        json={"full_name": "Ana Pérez", "headline": "Full Stack", "skills": "Python, React"},
    )
    assert res.status_code == 200
    assert res.json()["full_name"] == "Ana Pérez"

    again = client.get("/api/profile").json()
    assert again["skills"] == "Python, React"
    assert again["headline"] == "Full Stack"


def test_update_profile_ignores_none(client):
    client.put("/api/profile", json={"full_name": "Ana"})
    res = client.put("/api/profile", json={"phone": None, "location": "Bogotá"})
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Bogotá"
    assert data["full_name"] == "Ana"


def test_upload_cv_txt(client):
    files = {"file": ("cv.txt", b"Python React FastAPI SQL Docker", "text/plain")}
    res = client.post("/api/profile/cv", files=files)
    assert res.status_code == 200
    body = res.json()
    assert body["chars"] > 0
    assert "FastAPI" in body["profile"]["cv_text"]

    # El texto queda guardado en el perfil
    assert "FastAPI" in client.get("/api/profile").json()["cv_text"]


def test_upload_cv_unsupported_format(client):
    files = {"file": ("cv.exe", b"binary", "application/octet-stream")}
    res = client.post("/api/profile/cv", files=files)
    assert res.status_code == 400


def test_upload_cv_empty_text(client):
    files = {"file": ("cv.txt", b"   \n  ", "text/plain")}
    res = client.post("/api/profile/cv", files=files)
    assert res.status_code == 422
