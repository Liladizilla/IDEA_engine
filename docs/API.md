# API

Base URL in development: `http://localhost:8000` (`http://10.0.2.2:8000` from the Android emulator). Interactive docs at `/docs`.

Currently served from sample fixtures. Every response carries `is_sample: true`.

| Method | Path | Purpose |
|---|---|---|
| GET | /health | liveness |
| GET | /v1/bundle | everything the app's main screens need, one cacheable call |
| GET | /v1/home | top opportunities, new questions, niches |
| GET | /v1/opportunities?q=&min_score= | list, sorted by score |
| GET | /v1/opportunities/{id} | full detail with score breakdown and evidence |
| GET | /v1/radar | signals plus scopes with insufficient evidence |
| GET | /v1/niches | niches and categories |
| GET | /v1/discover?niche= | no niche: scan across categories. Niche with too little evidence returns `status: insufficient_signal` |

Errors are specific and safe to show, e.g. 404 "That opportunity no longer exists. It may have expired from the radar." Technical detail goes to logs.

Planned: auth (`/v1/auth/*`), `/v1/search` (semantic), `/v1/research/{id}`, `/v1/content-projects`, `/v1/me/usage`, and the public Intelligence API (opportunities, questions, clusters, trends, niches).
