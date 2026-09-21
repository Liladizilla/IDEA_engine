-- Run once against the database before the first migration.
CREATE EXTENSION IF NOT EXISTS vector;
-- After `alembic revision --autogenerate`, add an HNSW index for fast similarity search, e.g.:
-- CREATE INDEX ON questions USING hnsw (embedding vector_cosine_ops);
