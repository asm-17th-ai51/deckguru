import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.api import RecommendationResponse

_MOCK_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "mock_responses"
    / "recommend_deck_gold_stable.json"
)


async def run_strategy_agent(
    request_id: str,
    tier: str,
    play_style: str,
    question: str,
    *,
    patch_version: str,
    timeout_s: float = 25.0,
) -> RecommendationResponse:
    # TODO: Agent-1 구현 완료 후 아래 내용을 실제 LangGraph 호출로 교체.
    # from app.agents.strategy.graph import build_graph
    # graph = build_graph()
    # state = StrategyState(request_id=request_id, tier=tier, ...)
    # result = await graph.ainvoke(state)
    # return result.to_recommendation_response()
    data = json.loads(_MOCK_PATH.read_text(encoding="utf-8"))
    data["request_id"] = request_id
    data["patch_version"] = patch_version
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    return RecommendationResponse(**data)
