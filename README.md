# site-stats

A drop-in, admin-only stats page for any FastAPI app: traffic, unique visitors, errors, latency,
security events (failed logins, bot checks, rate limits) and whatever numbers your app wants to show.
One Python file, one dependency-free JS file, its own SQLite database. No raw IP addresses are kept.

## Add it to a project

1. Vendor it (copy `sitestats/` next to your app package) or install it:
   `pip install git+https://github.com/TamairNV/site-stats`
2. In the FastAPI app:

```python
from sitestats import Stats

stats = Stats("/data/stats.db")
stats.install(app, is_admin=lambda request: my_user(request).email in ADMIN_EMAILS)
```

   `install` adds the request-counting middleware and two routes: `GET /api/stats/data` (admins
   only; 404 for everyone else) and `GET /api/stats/dashboard.js` (the page code).
3. In the front end, wherever the admin should see it:

```js
const { renderStats } = await import('/api/stats/dashboard.js');
renderStats(element, { title: 'My app stats', fetchJson: (path) => myAuthedFetch(`/api/stats/${path}`) });
```

## Build on it

| You want | Do |
|---|---|
| A number on the page (users, orders, disk…) | `stats.gauge("Label", fn, group="Users")`: `fn()` runs when the page loads |
| Count something per day and list each one | `stats.event("kind", request, "detail")` + `stats.label("kind", "Readable name")` |
| A daily counter without the event log | `stats.count("key")` |
| Different admin rule | pass any `is_admin(request) -> bool` |
| Different URL | `stats.install(app, is_admin, prefix="/admin/stats")` |

Events show as totals (today / range) and as a "latest events" table with the address cut to
/24 (/48 for IPv6). Unique visitors are a hash of address + browser with a random salt that
changes every day and is never stored, so nobody can be tracked across days.

Data is kept 90 days (`Stats(path, keep_days=…)`); writes are batched every 10 s.
Behind Cloudflare it reads `CF-Connecting-IP`; only expose the app through Cloudflare (bind to
127.0.0.1) or that header could be faked.

## Try it

```
pip install fastapi uvicorn
uvicorn example.app:app
```

Used by: [fpv-spot-finder](https://github.com/TamairNV/fpv-spot-finder) (`server/sitestats`).
