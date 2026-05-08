"""ReAct의 reflect 단계.

역할:
- 지금까지 모은 Observation만으로 사용자의 질문에 답할 근거가 충분한지 판단한다.
- 충분하면 루프를 멈추고 extract 단계로 넘어간다.
- 부족하면 graph가 다음 plan step을 한 번 더 실행한다.

LLM이 없을 때도 서비스가 멈추면 안 되므로 `_fallback_reflect()`가 최소 규칙으로
판단한다.
"""

from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.strategy.llm import StrategyLLMError, call_structured
from app.research.state import ReflectDecision, ResearchState


SYSTEM_PROMPT = """Decide whether the collected observations are enough to answer
the user's TFT question with source-backed facts. Return structured output only."""


def _fallback_reflect(state: ResearchState) -> ReflectDecision:
    """LLM 없이 충분성 판단을 하는 보수적 규칙."""
    content_observations = [
        obs for obs in state.raw_observations
        if obs.url and len(obs.text.strip()) >= 120
    ]
    search_results = sum(
        len(obs.raw.get("results", []))
        for obs in state.raw_observations
        if obs.tool == "web_search"
    )
    if content_observations:
        # 실제 source page 본문을 하나라도 읽었다면 fact 추출을 시도할 가치가 있다.
        return ReflectDecision(enough=True, reason="Fetched at least one source page.")
    if search_results >= 3 and state.step >= 2:
        # 검색 snippet만 있어도 여러 결과가 있으면 최소 fallback fact를 만들 수 있다.
        return ReflectDecision(enough=True, reason="Collected multiple search snippets.")
    return ReflectDecision(enough=False, reason="Need at least one fetched source or more snippets.")


def fallback_reflect(state: ResearchState) -> ReflectDecision:
    """graph의 timeout fallback에서 직접 호출할 수 있도록 노출한 wrapper."""
    return _fallback_reflect(state)


def _state_summary(state: ResearchState) -> str:
    """LLM reflect에 넘길 최근 관찰 요약."""
    return json.dumps(
        {
            "question": state.question,
            "patch_version": state.patch_version,
            "observations": [
                {
                    "tool": obs.tool,
                    "url": str(obs.url) if obs.url else None,
                    "title": obs.title,
                    "text": obs.text[:800],
                }
                for obs in state.raw_observations[-6:]
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


async def reflect_research(state: ResearchState) -> ReflectDecision:
    """Solar structured output으로 충분성 판단을 받고, 실패하면 fallback을 쓴다."""
    try:
        return await call_structured(
            role="research",
            schema=ReflectDecision,
            messages=[
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=_state_summary(state)),
            ],
            retries=1,
        )
    except StrategyLLMError:
        # LLM 실패 시에도 ReAct 루프가 무한정 돌지 않도록 규칙 기반 판단으로 전환한다.
        return _fallback_reflect(state)
