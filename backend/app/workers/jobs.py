"""One collection cycle. Called by the scheduler, never from a request handler."""
from __future__ import annotations

from app.ai.base import AIProvider
from app.intelligence.pipeline import PipelineOutput, run_pipeline
from app.providers.base import CollectionResult, SourceProvider, collect_all


async def run_collection_cycle(
    providers: list[SourceProvider], embedder: Embedder | AIProvider, queries: list[str], per_query: int = 25, min_questions: int = 12, min_sources: int = 2
) -> tuple[PipelineOutput, CollectionResult]:
    merged = CollectionResult()
    for query in queries:
        got = await collect_all(providers, query, per_query)
        merged.items.extend(got.items)
        merged.errors.update(got.errors)
        merged.skipped = got.skipped
    seen, unique = set(), []
    for item in merged.items:  # the same item can match several queries
        key = (item.source, item.external_id)
        if key not in seen:
            seen.add(key)
            unique.append(item)
    merged.items = unique
    return await run_pipeline(unique, embedder, min_questions=min_questions, min_sources=min_sources), merged
