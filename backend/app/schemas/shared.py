from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl

from app.schemas.enums import Difficulty, Phase, SourceKind


class PlaybookStep(BaseModel):
    phase: Phase
    instruction: str = Field(min_length=1, max_length=200)


class Source(BaseModel):
    title: str
    url: str = Field(pattern=r"^https?://")
    published_at: datetime | None = None
    snippet: str = Field(max_length=200)
    source_kind: SourceKind


class DeckRecommendation(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    difficulty: Difficulty
    core_units: Annotated[list[str], Field(min_length=3, max_length=9)]
    key_items: Annotated[list[str], Field(min_length=1, max_length=6)]
    augment_direction: str = Field(max_length=120)
    playbook: Annotated[list[PlaybookStep], Field(min_length=1)]
    good_conditions: Annotated[list[str], Field(min_length=1)]
    avoid_conditions: list[str] = Field(default_factory=list)
    fallback_plan: str = Field(max_length=200)
    rationale: str = Field(max_length=300)


class DebugInfo(BaseModel):
    react_steps: int = 0
    rag_avg_score: float = 0.0
    tier2_triggered: bool = False
    node_latencies_ms: dict[str, int] = Field(default_factory=dict)
