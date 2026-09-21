# Environment

Copy `backend/.env.example` to `backend/.env`. Never commit `.env`.

| Variable | Needed for |
|---|---|
| DATABASE_URL, REDIS_URL | persistence and queues |
| JWT_SECRET | auth. 32+ characters in production |
| YOUTUBE_API_KEY | YouTube collector. Enable "YouTube Data API v3" in Google Cloud Console |
| REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT | Reddit collector (reddit.com/prefs/apps) |
| AI_PROVIDER, HF_TOKEN, HF_CHAT_MODEL, HF_EMBEDDING_MODEL, EMBEDDING_DIM | Hugging Face |
| OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_CHAT_MODEL | any OpenAI-compatible provider |
| LOCAL_AI_BASE_URL, LOCAL_AI_CHAT_MODEL | local model server |
| AI_DAILY_TOKEN_LIMIT_GLOBAL, AI_DAILY_TOKEN_LIMIT_PER_USER, AI_MONTHLY_COST_LIMIT_USD | cost control |
| ANSWERTHEPUBLIC_API_KEY, GOOGLE_TRENDS_API_KEY | optional providers |
| SENTRY_DSN, FIREBASE_PROJECT_ID | monitoring, push notifications |

Flutter build-time flags: `USE_MOCK` (default true), `API_BASE_URL`.
