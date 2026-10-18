def test_dashboard_empty(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["active"] == 0
    assert data["applied_this_week"] == 0
    assert data["avg_fit"] is None
    assert data["llm"] == "heuristic"
    assert data["by_status"] == {
        "guardada": 0,
        "aplicada": 0,
        "entrevista": 0,
        "oferta": 0,
        "rechazada": 0,
    }


def test_dashboard_counts(client):
    for i in range(3):
        client.post(
            "/api/applications",
            json={"company": f"Empresa {i}", "role": "Dev"},
        )
    first = client.get("/api/applications").json()["items"][0]
    client.patch(f"/api/applications/{first['id']}", json={"status": "aplicada"})

    data = client.get("/api/dashboard").json()
    assert data["total"] == 3
    assert data["active"] == 3
    assert data["by_status"]["aplicada"] == 1
    assert data["by_status"]["guardada"] == 2
    assert data["applied_this_week"] == 1
    assert len(data["recent"]) == 3
