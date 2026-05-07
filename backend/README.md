# DeckGuru Backend (51조)

`backend/`는 monorepo 내 Python 백엔드 — Strategy / RAG / Research 에이전트 + FastAPI gateway.

> **이 README는 Agent-1 (Strategy) 작업 진행 중 기준이며, RAG/Research는 stub만 있음.**
> Agent-2/3가 실제 구현으로 교체 예정.

---

## 디렉토리

```
backend/
├── pyproject.toml         # 단일 패키지 (Agent 1/2/3 + Backend가 공유)
├── .env.example           # 환경변수 템플릿 (.env는 git ignore)
├── app/
│   ├── schemas/           # 07-data-contracts.md 단일 진실 소스
│   │   ├── shared.py      # enum + Source/RagChunk/WebFact/Deck...
│   │   └── api.py         # RecommendRequest/Response
│   ├── agents/strategy/   # Agent-1 (본 PR)
│   │   ├── api.py         # run_strategy_agent — Backend의 단일 진입점
│   │   ├── state.py       # StrategyState (Pydantic v2)
│   │   ├── graph.py       # LangGraph StateGraph
│   │   ├── llm.py         # Upstage Solar 래퍼 (T=0, structured, retry)
│   │   ├── nodes/         # 7개 노드
│   │   └── prompts/       # 버전 관리 (manifest.yaml)
│   ├── rag/               # Agent-2 (현재 stub)
│   │   └── service.py     # RagService Protocol + InMemoryStubRagService
│   └── research/          # Agent-3 (현재 stub)
│       └── api.py         # run_live_research stub
└── tests/
    ├── conftest.py        # LLM mock fixture
    └── test_strategy_smoke.py
```

## 셋업

```bash
# Python 3.11 (D10 pin)
brew install python@3.11

cd backend
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env  # UPSTAGE_API_KEY 등 채우기
```

## 환경변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `UPSTAGE_API_KEY` | (필수) | Upstage Solar API key |
| `UPSTAGE_MODEL_RECOMMEND` | `solar-pro2` | recommend / analyze_meta 모델 |
| `UPSTAGE_MODEL_META` | `solar-pro2` | analyze_meta 모델 |
| `UPSTAGE_MODEL_INTENT` | `solar-mini` | analyze_intent (cheap) |
| `PATCH_VERSION` | `14.9` | 현재 패치 |
| `LIVE_RESEARCH_ENABLED` | `true` | Agent-3 폴백용 (false면 Live Research skip) |
| `DEMO_MODE` | `false` | true면 응답에 `debug` 필드 노출 |

## Strategy Agent 호출

Backend의 단일 진입점:

```python
from app.agents.strategy import run_strategy_agent  # alias of api.run_strategy_agent

response = await run_strategy_agent(
    request_id="...",
    tier="GOLD",
    play_style="stable_top4",
    question="...",
    patch_version="14.9",
    timeout_s=25.0,
)
# → RecommendationResponse (07-data-contracts §4)
```

타임아웃 시 `RecommendationTimeout` (Backend는 504 `agent_timeout`으로 매핑).

## 테스트

```bash
# Mock LLM smoke (네트워크 없이)
pytest tests/test_strategy_smoke.py -v

# 실제 Upstage 호출 (UPSTAGE_API_KEY 필요)
python -c "
import asyncio
from dotenv import load_dotenv; load_dotenv()
from app.agents.strategy.api import run_strategy_agent

async def main():
    r = await run_strategy_agent(
        request_id='live-1', tier='GOLD', play_style='stable_top4',
        question='현재 패치에서 골드가 티어 올리기 좋은 덱 추천해줘',
        patch_version='14.9', timeout_s=60.0,
    )
    print(r.model_dump_json(indent=2))

asyncio.run(main())
"
```

## 다른 팀원 통합 가이드

### Agent-2 (RAG)
- `app/rag/service.py` 의 `RagService` Protocol을 구현 (`ChromaRagService` 등).
- `app.agents.strategy.nodes.rag_retrieve.rag_retrieve` 시그니처: 키워드 인자 `rag` 로 주입 가능.
- 통합 위치: `backend/app/services/dependencies.py`에 DI 컨테이너 만들고 `default_rag_service`를 교체.

### Agent-3 (Research)
- `app/research/api.py` 의 `run_live_research` 만 같은 시그니처로 교체.
- `LIVE_RESEARCH_ENABLED=false` 로 Strategy를 RAG-only 모드로 강제 가능.

### Backend (FastAPI)
- `from app.agents.strategy import run_strategy_agent` 호출.
- `from app.schemas.api import RecommendRequest, RecommendationResponse` 사용.

## 노드 동작 요약 (02-spec §3)

| 노드 | LLM | 결정성 | 핵심 산출물 |
|---|---|---|---|
| `analyze_intent` | yes (intent 모델) | retry+fallback | `intent`, `extracted_keywords` |
| `rag_retrieve` | no | 100% | `rag_chunks`, `rag_avg_score` |
| `need_live?` (조건부 엣지) | no | 100% | live or skip 라우팅 |
| `live_research` | (sub-graph) | 부분 | `web_facts`, `sources` |
| `analyze_meta` | yes (meta 모델) | retry | `meta_summary`, `candidate_decks` |
| `recommend` | yes (recommend 모델) | retry | `final_decks` (검증 전) |
| `verify_grounding` | no | 100% | 화이트리스트 / 수치 / 금지어 필터 → confidence |
| `format_response` | no | 100% | `RecommendationResponse` |

## 알려진 제약

- Python 3.11 pin (D10). 3.12에서 동작은 하지만 팀 합의 전까진 3.11.
- `app/rag/service.py`는 InMemoryStub이라 검색 결과는 하드코딩된 5개 chunk.
- `app/research/api.py`는 빈 결과만 반환 — Live Research 트리거되면 `live_research_not_implemented` warning만 추가됨.
- 노드들은 `state.model_dump()`을 반환 (LangGraph가 in-place list mutation을 추적 못 하기 때문).

## 회귀 (구현 후 추가 예정)

- `evals/golden_set.jsonl` 20문항 (08-spec §1.1, Day 5/3)
- `tests/test_invariants.py` — 07-spec §4.1 의 I1~I10
- `tests/test_contracts.py` — fixture vs schema (07-spec §6.1)
