from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1
from app.api.auth import router as auth
from app.api.research import router as research
from app.api.content import router as content

app = FastAPI(title="IDEA API", version="0.1.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["GET", "POST"], allow_headers=["*"])
app.include_router(v1)
app.include_router(auth)
app.include_router(research)
app.include_router(content)


@app.get("/health")
async def health():
    return {"status": "ok"}
