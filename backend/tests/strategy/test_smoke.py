"""Smoke test — graph가 LLM 모킹 하에서 끝까지 도는지."""

from __future__ import annotations

import pytest

from app.agents.strategy.api import run_strategy_agent


pytestmark = pytest.mark.asyncio


async def test_recommend_deck_path(mock_llm):
    response = await run_strategy_agent(
        request_id="test-1",
        tier="GOLD",
        play_style="stable_top4",
        question="현재 패치에서 골드가 티어 올리기 좋은 덱 3개 추천해줘",
        patch_version="14.9",
    )
    assert response.intent == "recommend_deck"
    assert response.patch_version == "14.9"
    assert len(response.decks) >= 1
    deck = response.decks[0]
    assert deck.name == "정밀 리롤"
    # I1: core_units 가 화이트리스트(stub) 통과
    assert all(u in {"정밀의 사도", "기계 학자", "광신도", "라이트브링어",
                     "사이버시티 챔피언", "9코스트 정밀", "어둠의 화신",
                     "강철의 수호자", "드림리프 마법사"}
               for u in deck.core_units)
    # I8: playbook 에 phase 최소 1개
    assert len(deck.playbook) >= 1


async def test_other_intent_short_circuits(mock_llm):
    response = await run_strategy_agent(
        request_id="test-2",
        tier="IRON",
        play_style="easy_beginner",
        question="롤토체스 게임 처음 깔았는데 회원가입 어떻게 해?",
    )
    assert response.intent == "other"
    # I6: intent=other → decks 비어있고 안내 문구
    assert response.decks == []
    assert "지원 범위" in response.meta_summary
    # I4: decks==0 → confidence=low
    assert response.confidence == "low"


async def test_grounding_filters_unknown_units(mock_llm, monkeypatch):
    """recommend가 화이트리스트 외 unit을 뱉어도 verify_grounding이 제거."""
    from app.agents.strategy.nodes import recommend as rc_mod
    from app.agents.strategy.nodes.recommend import RecommendOut
    from app.schemas.shared import DeckRecommendation, PlaybookStep

    async def fake_with_unknown(role, schema, messages, retries=1):
        return RecommendOut(
            decks=[
                DeckRecommendation(
                    name="할루시 덱",
                    difficulty="medium",
                    core_units=["존재하지 않는 챔프", "또 다른 헛것", "환각 유닛"],
                    key_items=["없는 아이템"],
                    augment_direction="모름",
                    playbook=[PlaybookStep(phase="early", instruction="...")],
                    good_conditions=["..."],
                    avoid_conditions=[],
                    fallback_plan="...",
                    rationale="승률 100% 보장",
                )
            ]
        )

    monkeypatch.setattr(rc_mod, "call_structured", fake_with_unknown)

    response = await run_strategy_agent(
        request_id="test-3",
        tier="GOLD",
        play_style="stable_top4",
        question="추천해줘",
    )
    # 모두 걸러져서 빈 decks + low confidence
    assert response.decks == []
    assert response.confidence == "low"
    assert any(w.startswith("deck_filtered_") or w == "all_decks_filtered"
               for w in response.warnings)


async def test_determinism(mock_llm):
    """동일 입력 → 동일 응답 (generated_at 제외)."""
    r1 = await run_strategy_agent(
        request_id="rep-1", tier="GOLD", play_style="stable_top4",
        question="현재 패치 추천 덱", patch_version="14.9",
    )
    r2 = await run_strategy_agent(
        request_id="rep-1", tier="GOLD", play_style="stable_top4",
        question="현재 패치 추천 덱", patch_version="14.9",
    )
    d1 = r1.model_dump(exclude={"generated_at"})
    d2 = r2.model_dump(exclude={"generated_at"})
    assert d1 == d2
