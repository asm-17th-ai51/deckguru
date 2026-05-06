"""need_live? — 02-spec §3.3.

조건부 엣지에 사용되는 순수 함수. LLM 미사용.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from app.agents.strategy.state import StrategyState

FRESHNESS_KEYWORDS = ("이번 패치", "오늘", "최근", "어제", "현재 메타")


def _patch_age_days(patch_version: str) -> int:
    """패치 배포 일수. 정확한 매핑은 RAG/Backend 쪽 patch-info에서 보강.

    여기서는 환경변수 PATCH_RELEASED_AT (ISO date) 가 있으면 사용, 없으면 99로 fallback
    (오래된 패치로 간주 — 보수적).
    """
    iso = os.getenv("PATCH_RELEASED_AT")
    if not iso:
        return 99
    try:
        released = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - released
        return delta.days
    except ValueError:
        return 99


def need_live(state: StrategyState) -> bool:
    if state.intent in (None, "other"):
        return False
    if os.getenv("LIVE_RESEARCH_ENABLED", "true").lower() != "true":
        return False

    if state.rag_avg_score < 0.4:
        return True
    if any(k in state.question for k in FRESHNESS_KEYWORDS):
        return True
    if state.intent == "patch_summary" and _patch_age_days(state.patch_version) <= 3:
        return True
    return False


def need_live_branch(state: StrategyState) -> str:
    """LangGraph conditional edge용 라우팅 키."""
    return "live" if need_live(state) else "skip"
