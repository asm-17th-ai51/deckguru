"""live_research — 02-spec §3.4.

Agent-3의 sub-graph(`run_live_research`)를 호출하고 결과를 state에 병합.
타임아웃 15s. 초과 시 부분 결과 + warning.
"""

from __future__ import annotations

import asyncio
import logging

from app.agents.strategy.state import StrategyState
from app.research.api import run_live_research

logger = logging.getLogger(__name__)


async def live_research(state: StrategyState) -> dict:
    state.need_live = True
    try:
        result = await asyncio.wait_for(
            run_live_research(
                request_id=state.request_id,
                question=state.question,
                extracted_keywords=state.extracted_keywords,
                patch_version=state.patch_version,
                max_steps=5,
                timeout_s=15.0,
            ),
            timeout=15.0,
        )
    except asyncio.TimeoutError:
        logger.warning("live_research timeout")
        state.warnings.append("research_truncated")
        return state.model_dump()

    state.web_facts = result.web_facts
    state.sources.extend(result.sources)
    state.research_steps = result.research_steps
    state.warnings.extend(result.warnings)
    if result.truncated:
        state.warnings.append("research_truncated")

    return state.model_dump()
