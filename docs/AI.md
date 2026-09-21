# AI

`AIProvider` needs two methods per provider: `generate` and `embed`. `classify` and `summarize` are shared.

- `HuggingFaceProvider`: chat through `https://router.huggingface.co/v1` (OpenAI-compatible), embeddings through `huggingface_hub` feature extraction. Free credits are limited. Check current pricing and which models your account can reach before relying on it.
- `OpenAICompatibleProvider`: any `/chat/completions` server.
- `LocalAIProvider`: Ollama, llama.cpp or vLLM on your machine.

Switch with `AI_PROVIDER`. Nothing else changes.

Rules the code enforces
- Prompts (`ai/prompts.py`) require evidence-only claims and JSON output.
- `parse_model` raises `AIParseError` on bad output. It never guesses.
- `generate_ideas` returns `InsufficientSignal` without calling the model when evidence is thin.
- `MeteredAIProvider` wraps any provider with `AIUsageService`: global daily tokens, per-user daily tokens, monthly cost, per-provider request caps. A worker that loops hits `BudgetExceeded`, not your budget. Set `price_per_1k_tokens` per model to get cost limits.

Not done yet: answer-quality assessment (until then the score treats answer quality as neutral and says so in the factor note), audience-value scoring from the creator profile, the research and script generators.
