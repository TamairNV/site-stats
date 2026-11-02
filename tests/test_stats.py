from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from sitestats import Stats, mask_ip, route_of


def make(tmp_path):
    app = FastAPI()
    stats = Stats(tmp_path / "s.db", flush_every=3600)
    stats.install(app, is_admin=lambda r: r.headers.get("authorization") == "Bearer ok")
    stats.gauge("Answer", lambda: 42, "Example")
    stats.label("hello", "Said hello")

    @app.get("/api/hello/{x}")
    def hello(x: str, request: Request):
        stats.event("hello", request, x)
        return {"x": x}
    return app, stats


def test_admin_only_and_counts(tmp_path):
    app, stats = make(tmp_path)
    c = TestClient(app)
    for i in range(3):
        c.get(f"/api/hello/{i}abc")
    c.get("/nope")
    assert c.get("/api/stats/data").status_code == 404
    d = c.get("/api/stats/data?days=7", headers={"Authorization": "Bearer ok"}).json()
    today = d["days"][-1]
    assert today["requests"] == 4 and today["errors"] == 1 and today["visitors"] == 1
    assert dict(d["paths_today"])["/api/hello/:id"] == 3
    assert d["gauges"] == [{"label": "Answer", "value": 42, "group": "Example"}]
    assert d["events"][0]["label"] == "Said hello"
    assert c.get("/api/stats/dashboard.js").status_code == 200


def test_privacy_helpers():
    assert mask_ip("81.2.69.160") == "81.2.69.0/24"
    assert mask_ip("2001:db8:1:2::1") == "2001:db8:1::/48"
    assert mask_ip("junk") == "?"
    assert route_of("/api/photos/aZ3_kd93kfjslq0q2kd8.jpg") == "/api/photos/:id"
