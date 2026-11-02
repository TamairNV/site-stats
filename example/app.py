"""Smallest working example: uvicorn example.app:app, then open http://127.0.0.1:8000/
(the token here is 'letmein'; a real app checks its own login)."""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from sitestats import Stats

app = FastAPI()
stats = Stats("stats.db")
stats.install(app, is_admin=lambda req: req.headers.get("authorization") == "Bearer letmein")
stats.gauge("Answer", lambda: 42, group="Example")
stats.label("hello", "Someone said hello")


@app.get("/api/hello")
def hello(request: Request):
    stats.event("hello", request, "from the example")
    return {"hi": True}


@app.get("/", response_class=HTMLResponse)
def page():
    return """<!doctype html><meta charset=utf-8><body style="background:#101519;padding:20px"><div id=s></div>
<script type=module>
const { renderStats } = await import('/api/stats/dashboard.js');
renderStats(document.getElementById('s'), { title: 'Example stats',
  fetchJson: (p) => fetch('/api/stats/' + p, { headers: { Authorization: 'Bearer letmein' } }).then((r) => r.json()) });
</script>"""
