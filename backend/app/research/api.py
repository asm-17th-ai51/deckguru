"""Live Research interface.

소유: Agent-3 (04-agent-research-spec.md).
호출자: Agent-1 (Strategy).

본 파일의 `run_live_research`가 인터페이스 계약(08-roles-and-handoffs §2.3).
실제 구현은 ReAct sub-graph + Tavily/fetch_page/youtube_transcript.
Agent-3 구현 머지 전에는 빈 결과를 반환 — Strategy Agent의 RAG-only 경로 검증용.
"""

from __future__ import annotations

import os

from pydantic import BaseModel, Field

from app.schemas.shared import Source, WebFact


class ResearchResult(BaseModel):
    web_facts: list[WebFact] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    research_steps: int = 0
    truncated: bool = False
    warnings: list[str] = Field(default_factory=list)


async def run_live_research(
    request_id: str,
    *,
    question: str,
    extracted_keywords: list[str],
    patch_version: str,
    max_steps: int = 5,
    timeout_s: float = 15.0,
) -> ResearchResult:
    """Live Research 진입점 — Agent-3 구현 자리.

    `LIVE_RESEARCH_ENABLED=false` 환경변수면 즉시 빈 결과로 폴백.
    구현 미완 상태이므로 현재는 항상 빈 결과 + warning 반환.
    """
    if os.getenv("LIVE_RESEARCH_ENABLED", "true").lower() != "true":
        return ResearchResult(warnings=["live_research_disabled_by_env"])

    # TODO(Agent-3): ReAct sub-graph 구현으로 교체.
    return ResearchResult(warnings=["live_research_not_implemented"])
