# Database

PostgreSQL 16 with pgvector. `docker compose up -d` starts one (with the extension enabled).

Tables: users, creator_profiles, sources, source_items, questions, question_clusters, signals, trend_snapshots,
opportunities, ideas, saved_items, research_reports, content_projects, ai_requests, provider_usage.

Migrations
```bash
cd backend
alembic init migrations        # once; set sqlalchemy.url and target_metadata = app.database.models.Base.metadata
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
Then add a vector index once you have data: `CREATE INDEX ON questions USING hnsw (embedding vector_cosine_ops);`

`EMBEDDING_DIM` (default 384) must match the embedding model. Changing models means re-embedding and a new column or migration.

`opportunities.factors` stores the full explainable breakdown as JSON so an old score can always be explained even after weights change.
`trend_snapshots` gets one row per cluster per day, which is what velocity is computed from.
