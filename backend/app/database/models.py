"""Core tables (spec section 41). PostgreSQL + pgvector. Generate migrations with Alembic autogenerate."""
from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import get_settings

EMBED_DIM = get_settings().embedding_dim
JsonType = JSON().with_variant(JSONB(), "postgresql")


class Base(DeclarativeBase):
    pass


def _id() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _now() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = _id()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    locale: Mapped[str] = mapped_column(String(8), default="en")
    plan: Mapped[str] = mapped_column(String(16), default="free")
    created_at: Mapped[datetime] = _now()
    profile: Mapped["CreatorProfile"] = relationship(back_populates="user", uselist=False)


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"
    id: Mapped[uuid.UUID] = _id()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    niche: Mapped[str | None] = mapped_column(String(160))
    audience: Mapped[str | None] = mapped_column(Text)
    platforms: Mapped[list] = mapped_column(JsonType, default=list)
    language: Mapped[str] = mapped_column(String(8), default="en")
    tone: Mapped[str | None] = mapped_column(String(64))
    preferred_format: Mapped[str | None] = mapped_column(String(32))
    excluded_topics: Mapped[list] = mapped_column(JsonType, default=list)
    covered_topics: Mapped[list] = mapped_column(JsonType, default=list)
    notify_mode: Mapped[str] = mapped_column(String(24), default="daily_digest")
    user: Mapped[User] = relationship(back_populates="profile")


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[uuid.UUID] = _id()
    kind: Mapped[str] = mapped_column(String(32), index=True)  # youtube | reddit | rss ...
    name: Mapped[str] = mapped_column(String(160))
    config: Mapped[dict] = mapped_column(JsonType, default=dict)


class SourceItem(Base):
    __tablename__ = "source_items"
    __table_args__ = (UniqueConstraint("source", "external_id"), Index("ix_source_items_created", "created_at"))
    id: Mapped[uuid.UUID] = _id()
    source: Mapped[str] = mapped_column(String(32))
    external_id: Mapped[str] = mapped_column(String(160))
    title: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, default="")
    url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    engagement: Mapped[dict] = mapped_column(JsonType, default=dict)
    item_metadata: Mapped[dict] = mapped_column("metadata", JsonType, default=dict)
    embedding = mapped_column(Vector(EMBED_DIM), nullable=True)
    collected_at: Mapped[datetime] = _now()


class QuestionCluster(Base):
    __tablename__ = "question_clusters"
    id: Mapped[uuid.UUID] = _id()
    representative_question: Mapped[str] = mapped_column(Text)
    audience: Mapped[str | None] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(64))
    question_count: Mapped[int] = mapped_column(Integer, default=0)
    source_count: Mapped[int] = mapped_column(Integer, default=0)
    growth: Mapped[float] = mapped_column(Float, default=0)
    velocity: Mapped[str] = mapped_column(String(16), default="unknown")
    centroid = mapped_column(Vector(EMBED_DIM), nullable=True)
    updated_at: Mapped[datetime] = _now()
    questions: Mapped[list["Question"]] = relationship(back_populates="cluster")


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[uuid.UUID] = _id()
    cluster_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("question_clusters.id"), index=True)
    source_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_items.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    signal_type: Mapped[str] = mapped_column(String(24))
    problem: Mapped[str | None] = mapped_column(Text)
    audience: Mapped[str | None] = mapped_column(Text)
    dissatisfied: Mapped[bool] = mapped_column(default=False)
    embedding = mapped_column(Vector(EMBED_DIM), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cluster: Mapped[QuestionCluster | None] = relationship(back_populates="questions")


class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[uuid.UUID] = _id()
    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_clusters.id"), index=True)
    detected_at: Mapped[datetime] = _now()
    momentum: Mapped[float] = mapped_column(Float, default=0)
    sources: Mapped[list] = mapped_column(JsonType, default=list)


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"
    id: Mapped[uuid.UUID] = _id()
    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_clusters.id"), index=True)
    day: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    signal_count: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("cluster_id", "day"),)


class Opportunity(Base):
    __tablename__ = "opportunities"
    id: Mapped[uuid.UUID] = _id()
    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_clusters.id"), index=True)
    title: Mapped[str] = mapped_column(Text)
    audience: Mapped[str | None] = mapped_column(Text)
    overall_score: Mapped[int] = mapped_column(Integer, index=True)
    confidence: Mapped[str] = mapped_column(String(8))
    factors: Mapped[list] = mapped_column(JsonType, default=list)  # full explainable breakdown
    detected_at: Mapped[datetime] = _now()
    embedding = mapped_column(Vector(EMBED_DIM), nullable=True)


class Idea(Base):
    __tablename__ = "ideas"
    id: Mapped[uuid.UUID] = _id()
    opportunity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    payload: Mapped[dict] = mapped_column(JsonType)
    created_at: Mapped[datetime] = _now()


class SavedItem(Base):
    __tablename__ = "saved_items"
    id: Mapped[uuid.UUID] = _id()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"))
    state: Mapped[str] = mapped_column(String(16), default="saved")  # saved | dismissed | published
    created_at: Mapped[datetime] = _now()
    __table_args__ = (UniqueConstraint("user_id", "opportunity_id"),)


class ResearchReport(Base):
    __tablename__ = "research_reports"
    id: Mapped[uuid.UUID] = _id()
    opportunity_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    body: Mapped[dict] = mapped_column(JsonType)  # every claim keeps a source reference
    created_at: Mapped[datetime] = _now()


class ContentProject(Base):
    __tablename__ = "content_projects"
    id: Mapped[uuid.UUID] = _id()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    opportunity_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("opportunities.id"))
    format: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="draft")
    body: Mapped[dict] = mapped_column(JsonType, default=dict)
    created_at: Mapped[datetime] = _now()


class AIRequest(Base):
    __tablename__ = "ai_requests"
    id: Mapped[uuid.UUID] = _id()
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), index=True)
    provider: Mapped[str] = mapped_column(String(32))
    model: Mapped[str] = mapped_column(String(160))
    operation: Mapped[str] = mapped_column(String(32))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = _now()


class ProviderUsage(Base):
    """Daily rollup per provider (YouTube quota units, Reddit calls, AI tokens)."""

    __tablename__ = "provider_usage"
    id: Mapped[uuid.UUID] = _id()
    provider: Mapped[str] = mapped_column(String(32))
    day: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    units: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("provider", "day"),)


class Job(Base):
    """Async job tracking (research, content generation, etc.)."""

    __tablename__ = "jobs"
    id: Mapped[uuid.UUID] = _id()
    type: Mapped[str] = mapped_column(String(32), index=True)  # research | content
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending | running | completed | failed
    payload: Mapped[dict] = mapped_column(JsonType, default=dict)
    result: Mapped[dict | None] = mapped_column(JsonType, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = _now()
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
