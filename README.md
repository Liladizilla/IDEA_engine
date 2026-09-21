# IDEA

Find what people want to know. Create what they want to watch.

IDEA reads public questions (YouTube, Reddit, later more), groups them, checks what answers already exist,
and scores the gaps with a score you can always explain. AI helps interpret evidence. It never invents it.

```
idea/
  backend/   FastAPI, collectors, intelligence engine, AI providers, tests
  mobile/    Flutter Android app (mock data by default)
  docs/      ARCHITECTURE, API, DATABASE, AI, DATA_SOURCES, SECURITY, DEPLOYMENT, ENVIRONMENT, CONTRIBUTING
  preview/   the HTML design preview (same tokens, icons and data as the app)
```

## What works today

| Area | State |
|---|---|
| Scoring engine (9 factors, explainable, insufficient-signal gate) | ✅ Built, tested, production-ready |
| Question extraction, dissatisfaction detection, clustering, trend velocity | ✅ Built, tested (hashing embedder for tests; real embeddings via AIProvider) |
| YouTube collector | ✅ Built, fetching 150+ items/query with real API key |
| AI providers (Hugging Face, OpenAI-compatible, local) + usage limits | ✅ Built, tested with real embeddings (all-MiniLM-L6-v2, 384-dim) |
| Auth (argon2, JWT access + refresh tokens) | ✅ Built, tested, routes wired |
| DB models (15 tables, pgvector) | ✅ Migrated, production schema |
| API | ✅ All `/v1/*` endpoints serving real database data (`is_sample: false`) |
| Research pipeline | ✅ Async jobs: start → background process → report retrieval |
| Flutter app | ✅ All screens, 18 components, `flutter analyze` clean, **APK built** |

Sample data is flagged `is_sample: true` and the app shows a "Sample data" strip. It is never presented as evidence.

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your keys (YOUTUBE_API_KEY required)
PYTHONPATH=. pytest -q        # 46 tests pass
uvicorn app.main:app --reload # http://localhost:8000/docs
```

### Database
```bash
# Start PostgreSQL + pgvector + Redis (via podman/docker)
podman-compose up -d
# Run migration
alembic upgrade head
```

### Run Collection Pipeline
```bash
# Single collection cycle (collect → embed → cluster → score → persist)
cd backend
PYTHONPATH=. python -m app.workers.scheduler
```

### Mobile (Android)
```bash
cd mobile
flutter pub get
# Mock data (no backend needed)
flutter run
# Real backend data
flutter run --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=http://10.0.2.2:8000
# Build release APK
flutter build apk --release --dart-define=API_BASE_URL=http://10.0.2.2:8000 --dart-define=USE_MOCK=false
```

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /v1/bundle` | Complete app data (opportunities, radar, categories) |
| `GET /v1/home` | Home screen: top 3 opportunities |
| `GET /v1/opportunities` | Paginated list with search & score filter |
| `GET /v1/opportunities/{id}` | Full detail with evidence, trend, factors |
| `GET /v1/radar` | Real-time signals (last 24h) |
| `GET /v1/niches` | Category discovery |
| `GET /v1/discover` | Niche analysis |
| `POST /v1/auth/register` | Register user |
| `POST /v1/auth/login` | Login, returns access + refresh tokens |
| `POST /v1/opportunities/{id}/research` | Start async research job (202) |
| `GET /v1/jobs/{id}` | Poll job status |
| `GET /v1/opportunities/{id}/research` | Get completed research report |

## Architecture Highlights

- **9-factor scoring**: demand, question_density, growth, dissatisfaction, engagement, audience_value, recency, competition, answer_saturation
- **Explainable**: every score point traced to a factor with weight, value, and rationale
- **Insufficient-signal gate**: clusters below threshold auto-flagged, never presented as opportunities
- **Vector search**: pgvector + HNSW for semantic clustering
- **Async research**: background jobs with status polling, LLM-generated briefs
- **Clean architecture**: FastAPI + SQLAlchemy 2.0 + Pydantic v2, Riverpod + Flutter

## Download

Latest release APK: [Releases](https://github.com/Liladizilla/IDEA_engine/releases)

## License

MIT