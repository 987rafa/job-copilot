def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["llm"] == "heuristic"


def test_health_alias(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_root(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Job Copilot"
    assert "version" in data
