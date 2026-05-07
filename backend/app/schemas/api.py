from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.enums import Confidence, Intent, PlayStyle, Tier
from app.schemas.shared import DebugInfo, DeckRecommendation, Source


class RecommendRequest(BaseModel):
    tier: Tier
    play_style: PlayStyle
    question: str = Field(min_length=1, max_length=500)


class RecommendationResponse(BaseModel):
    request_id: str
    patch_version: str
    intent: Intent
    meta_summary: str = Field(max_length=400)
    decks: Annotated[list[DeckRecommendation], Field(max_length=3)]
    sources: list[Source]
    confidence: Confidence
    warnings: list[str] = Field(default_factory=list)
    generated_at: datetime
    debug: DebugInfo = Field(default_factory=DebugInfo)


class FeedbackRequest(BaseModel):
    request_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)
    deck_clicked: str | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
