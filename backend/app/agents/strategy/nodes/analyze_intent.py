"""analyze_intent — 02-spec §3.1.

LLM(small, T=0)으로 사용자 질문을 5개 enum + 키워드로 분류.
schema fail → 1회 retry → fallback intent=other.
"""

from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.agents.strategy.llm import StrategyLLMError, call_structured
from app.agents.strategy.prompts import load_json
from app.agents.strategy.state import StrategyState
from app.schemas.shared import Intent

logger = logging.getLogger(__name__)


class IntentOut(BaseModel):
    intent: Intent
    extracted_keywords: list[str] = Field(default_factory=list, max_length=5)


def _build_messages(question: str) -> list:
    cfg = load_json("intent")
    examples = cfg["examples"]
    fewshot = "\n".join(
        f'Question: {ex["q"]}\nResult: {{"intent":"{ex["intent"]}","extracted_keywords":{json.dumps(ex["extracted_keywords"], ensure_ascii=False)}}}'
        for ex in examples
    )
    sys_prompt = cfg["system"] + "\n\n[Examples]\n" + fewshot
    return [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"Question: {question}\nResult:"),
    ]


async def analyze_intent(state: StrategyState) -> dict:
    try:
        result = await call_structured(
            role="intent",
            schema=IntentOut,
            messages=_build_messages(state.question),
            retries=1,
        )
        state.intent = result.intent
        state.extracted_keywords = result.extracted_keywords
    except StrategyLLMError as exc:
        logger.warning("analyze_intent fallback to 'other': %s", exc)
        state.intent = "other"
        state.warnings.append("intent_classification_failed")

    return state.model_dump()
