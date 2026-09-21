# Architecture

```
Flutter UI -> Riverpod -> IdeaRepository -> Dio -> FastAPI
                                                     |
SourceProvider[] -> RawItem -> questions -> embeddings -> clusters -> stats -> score -> opportunities (Postgres + pgvector)
```

Principles
- Evidence first. AI interprets supplied evidence. It never supplies it. Prompts forbid invention and parsing rejects malformed output rather than repairing it.
- Providers are replaceable. Sources implement `SourceProvider`, trends implement `TrendProvider`, models implement `AIProvider`. The engine imports none of the concrete classes.
- One provider failing never blocks the others (`collect_all`).
- Not enough evidence means `InsufficientSignal`, not a weaker score. Minimum 12 questions and 2 sources per cluster.
- Heavy work runs in workers (`app/workers`), never in request handlers.

Backend map
- `collectors/` YouTube, Reddit, RSS, trends, AnswerThePublic (stub)
- `intelligence/` questions, dissatisfaction, clustering, velocity, scoring, pipeline
- `ai/` providers, prompts, ideas, embeddings, usage limits
- `database/` models and session. `security/` passwords, tokens. `api/` routes. `workers/` jobs, scheduler

Videos are treated as existing answers (competition and coverage), not as demand. Questions come from comments, posts and feeds.

Mobile map: `core/` theme, icons, widgets, router, strings. `domain/` models. `data/` repository and providers. `features/` one folder per screen.
