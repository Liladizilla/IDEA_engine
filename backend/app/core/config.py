"""Settings. Every secret lives here (server side) and never in the Flutter app."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://idea:idea@localhost:5432/idea"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = ""

    youtube_api_key: str = ""
    youtube_daily_quota_budget: int = 8000

    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "idea-app/0.1"

    ai_provider: str = "huggingface"
    hf_token: str = ""
    hf_chat_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    hf_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_chat_model: str = ""
    local_ai_base_url: str = "http://localhost:11434/v1"
    local_ai_chat_model: str = ""

    ai_daily_token_limit_global: int = 500_000
    ai_daily_token_limit_per_user: int = 40_000
    ai_monthly_cost_limit_usd: float = 25.0

    answerthepublic_api_key: str = ""
    google_trends_api_key: str = ""
    sentry_dsn: str = ""
    firebase_project_id: str = ""

    rss_feed_urls: str = ""  # comma-separated list of RSS/Atom feed URLs

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and len(settings.jwt_secret) < 32:
        raise RuntimeError("JWT_SECRET must be set (32+ chars) in production")
    return settings
