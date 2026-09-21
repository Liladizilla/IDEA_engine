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
| Scoring engine (9 factors, explainable, insufficient-signal gate) | Built, tested |
| Question extraction, dissatisfaction detection, clustering, trend velocity | Built, tested (hashing embedder for tests; real embeddings via AIProvider) |
| YouTube and Reddit collectors, RSS collector | Built, tested against mocked HTTP. Not yet run with real keys |
| AI providers (Hugging Face, OpenAI-compatible, local) + usage limits | Built, tested against mocked HTTP |
| Auth primitives (argon2, JWT access + refresh) | Built, tested. No auth routes yet |
| DB models (15 tables, pgvector) | Written, imports cleanly. No migrations generated yet |
| API | Serves sample data from `/v1/*`. Pipeline is not wired to the database yet |
| Flutter app | All screens and 18 components written against the sample data. Syntax-checked, **not compiled** (no Flutter SDK where this was built). Expect a few small fixes on first `flutter analyze` |

Sample data is flagged `is_sample: true` and the app shows a "Sample data" strip. It is never presented as evidence.

## Run it

Backend:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your keys
PYTHONPATH=. pytest -q        # 46 tests
uvicorn app.main:app --reload # http://localhost:8000/docs
```
Database (when you are ready to persist): `docker compose up -d`

Mobile:
```bash
cd mobile
./tool/bootstrap.sh           # flutter create (android only), pub get, launcher icons, manifest
flutter run                   # mock data
flutter run --dart-define=USE_MOCK=false --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

## Next, in order (spec section 77)

1. Run `flutter analyze`, fix whatever it finds, run the app.
2. Add `YOUTUBE_API_KEY`, run a real collection cycle (`python -m app.workers.scheduler`), read the printed counts.
3. Persist: Alembic migration, save source items, questions, clusters, opportunities.
4. Swap `HashingEmbedder` for `AIProvider.embed` and store vectors in pgvector.
5. Replace `/v1/bundle` sample data with database reads. Delete the sample path.
6. Research, content generation, then everything in the spec's phases 2 to 4.
