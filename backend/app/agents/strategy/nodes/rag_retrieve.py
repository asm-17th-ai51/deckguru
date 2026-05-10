"""rag_retrieve — 02-spec §3.2.

intent별 query plan으로 RAG Service 호출. patch_version 필터 강제.
LLM 미사용. 100% 결정적.
"""

from __future__ import annotations

import logging

from app.agents.strategy.state import StrategyState
from app.rag.service import RagService, get_rag_service
from app.schemas.shared import IndexName, RagChunk

logger = logging.getLogger(__name__)

# (index, query 템플릿, k). query 템플릿은 {q}, {kw} placeholder 지원.
QUERY_PLAN: dict[str, list[tuple[IndexName, str, int]]] = {
    "recommend_deck": [
        ("deck_templates", "{q}", 5),
        ("augments", "{q}", 3),
        ("traits", "{q}", 3),
    ],
    "deck_playstyle": [
        ("deck_templates", "{kw}", 1),
        ("playbook", "{q}", 5),
        ("units", "{kw}", 3),
    ],
    "item_pivot": [
        ("items", "{kw}", 5),
        ("deck_templates", "{kw}", 3),
        ("units", "{kw}", 3),
    ],
    "patch_summary": [
        ("patch_summary", "{q}", 8),
        ("deck_templates", "{q}", 3),
    ],
}


def _format_query(template: str, *, question: str, keywords: list[str]) -> str:
    kw = " ".join(keywords) if keywords else question
    return template.format(q=question, kw=kw)


def _build_plan(state: StrategyState) -> list[tuple[IndexName, str, int]]:
    if state.intent is None or state.intent == "other":
        return []
    raw = QUERY_PLAN.get(state.intent, [])
    return [
        (idx, _format_query(tpl, question=state.question, keywords=state.extracted_keywords), k)
        for idx, tpl, k in raw
    ]


def _avg_top3(chunks: list[RagChunk]) -> float:
    if not chunks:
        return 0.0
    top3 = sorted(chunks, key=lambda c: c.score, reverse=True)[:3]
    return sum(c.score for c in top3) / len(top3)


async def rag_retrieve(
    state: StrategyState,
    *,
    rag: RagService | None = None,
) -> dict:
    plan = _build_plan(state)
    if not plan:
        return state.model_dump()

    active_rag = rag or get_rag_service()
    chunks = active_rag.multi_search(plan, patch_version=state.patch_version)
    state.rag_chunks = chunks
    state.rag_avg_score = _avg_top3(chunks)

    if state.rag_avg_score < 0.4:
        state.warnings.append("rag_avg_score_low")

    logger.debug(
        "rag_retrieve intent=%s n_chunks=%d avg=%.3f",
        state.intent, len(chunks), state.rag_avg_score,
    )
    return state.model_dump()
