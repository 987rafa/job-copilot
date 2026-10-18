def test_reset_seeds_demo_data(client):
    res = client.post("/api/demo/reset")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["applications"] == 8
    assert body["drafts"] == 3

    profile = client.get("/api/profile").json()
    assert profile["full_name"] == "Camila Restrepo"
    assert "React" in profile["skills"]


def test_reset_twice_keeps_counts(client):
    client.post("/api/demo/reset")
    client.post("/api/demo/reset")

    data = client.get("/api/dashboard").json()
    assert data["total"] == 8
    assert data["by_status"] == {
        "guardada": 2,
        "aplicada": 2,
        "entrevista": 2,
        "oferta": 1,
        "rechazada": 1,
    }
    assert data["applied_this_week"] == 3
    assert data["avg_fit"] is not None
    assert len(data["upcoming_followups"]) >= 2

    drafts = client.get("/api/ai/drafts").json()
    assert len(drafts) == 3
