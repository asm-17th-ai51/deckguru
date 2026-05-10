# 09. 실제 Strategy/RAG 추천 파이프라인 구현 계획

> 목표: `/api/recommend`가 mock fixture 대신 실제 Strategy Agent를 호출하고, Strategy Agent가 Chroma 기반 RAG 검색 결과로 grounded 추천을 생성하도록 전환합니다.
> 범위: backend 추천 경로, Chroma-backed `RagService`, RAG build CLI, health/patch-info 계약, 테스트 보강입니다.
> 제외: YouTube transcript 도구와 관련 의존성은 프록시/네트워크 안정성 확인 전까지 이번 범위에서 제외합니다.

---

## 1. 현재 확인된 구현 상태

| 영역 | 현재 상태 | 구현 계획에 반영할 점 |
| --- | --- | --- |
| 추천 라우터 | `backend/app/api/recommend.py`는 `app.services.strategy_invoker.run_strategy_agent`를 호출합니다. timeout은 504로 매핑하지만 일반 예외는 500 `agent_internal`로만 반환합니다. | Strategy/RAG 실패 유형별 예외를 라우터에서 구분해 `agent_timeout`, `agent_failed`, `rag_unavailable`, `agent_internal`로 매핑합니다. |
| Strategy invoker | `backend/app/services/strategy_invoker.py`는 `tests/fixtures/mock_responses/recommend_deck_gold_stable.json`을 읽어 `RecommendationResponse`를 반환합니다. | runtime 기본 경로에서 fixture 반환을 제거하고 `app.agents.strategy.api.run_strategy_agent` 호출로 교체합니다. fixture는 테스트 monkeypatch 또는 명시적 demo/mock flag 뒤에만 둡니다. |
| Strategy Agent API | `backend/app/agents/strategy/api.py`에는 실제 LangGraph `COMPILED_GRAPH.ainvoke()` 진입점과 `RecommendationTimeout`, `RecommendationFailed` 예외가 있습니다. | backend service wrapper는 이 진입점을 호출하고, 예외 의미를 FastAPI error code로 보존합니다. RAG 접근 실패용 예외는 추가로 정의합니다. |
| RAG Service | `backend/app/rag/service.py`는 `RagService` Protocol과 `InMemoryStubRagService` 기본 인스턴스를 제공합니다. Chroma 구현은 아직 없습니다. | 기본 runtime 의존성을 Chroma-backed 구현으로 바꾸고, stub은 테스트 전용 또는 demo flag 경로로 낮춥니다. |
| Strategy RAG 노드 | `backend/app/agents/strategy/nodes/rag_retrieve.py`는 `default_rag_service`를 기본 인자로 받아 `multi_search()`를 호출합니다. | import-time 기본 인스턴스 고정을 피하고, 실제 `RagService` 주입 지점을 명확히 만듭니다. |
| RAG 데이터 | `data/rag/processed/patch_summary/17.2.jsonl`, `data/rag/processed/deck_templates/17.2b.jsonl`만 실제 데이터가 있습니다. 나머지 인덱스는 `.gitkeep` 중심입니다. | 1차 구현은 기존 두 인덱스 upsert부터 지원합니다. 빈 인덱스 데이터 보강은 후속 작업으로 분리합니다. |
| patch manifest | `current_patch.json`에는 `current_patch`, `record_count`, `sources`, `jsonl_path`가 있지만 `last_updated`/`fetched_at`이 없습니다. | build/refresh CLI가 `last_updated` 또는 `fetched_at`과 source metadata를 기록하도록 manifest 계약을 보강합니다. |
| patch source of truth | `backend/app/settings.py`의 `patch_version` 기본값은 `14.9`이고, 현재 RAG 데이터는 `17.2`/`17.2b`입니다. | `PATCH_VERSION` 기본값과 로컬 `.env` 예시를 `17.2` 기준으로 맞춥니다. |
| health | `backend/app/api/health.py`는 Chroma collection이 아니라 processed JSONL line count를 셉니다. | Chroma collection count 기준으로 전환하고, Chroma 부재 또는 빈 collection이 있으면 `degraded`를 반환합니다. |
| Live Research | `web_search`와 `fetch_page` 기반 흐름이 구현되어 있습니다. `ToolName`에는 `web_search`, `fetch_page`만 포함됩니다. | 현재 흐름을 유지합니다. YouTube transcript는 문서와 코드 범위에서 deferred로 명시합니다. |

---

## 2. 구현 목표와 비목표

### 2.1 구현 목표

1. `/api/recommend`가 기본 runtime에서 mock fixture를 반환하지 않게 합니다.
2. Strategy Agent가 Chroma-backed `RagService`를 사용해 `RagChunk`를 조회합니다.
3. RAG 검색은 patch family, `all` fallback, score 정렬, 중복 제거, low-score 필터를 지원합니다.
4. RAG build CLI로 processed JSONL을 Chroma collection에 재생성할 수 있게 합니다.
5. `/api/health`와 `/api/patch-info`가 Chroma/manifest 상태를 실제로 반영하게 합니다.
6. mock 제거 이후에도 CI가 LLM monkeypatch와 실제 RAG fixture 조합으로 안정적으로 검증되게 합니다.

### 2.2 비목표

- 8개 RAG 인덱스의 전체 데이터 완성은 이번 범위에서 제외합니다.
- Chroma vectorstore 산출물은 repo에 커밋하지 않습니다.
- YouTube transcript 파일, 도구, 의존성은 추가하지 않습니다.
- Upstage API 키가 없는 환경에서 실제 LLM E2E를 CI 기본 경로로 요구하지 않습니다.

---

## 3. Backend 추천 경로 전환

### 3.1 호출선 변경

`backend/app/services/strategy_invoker.py`는 fixture를 직접 읽지 않고 `app.agents.strategy.api.run_strategy_agent`를 호출합니다.

```python
from app.agents.strategy.api import (
    RecommendationFailed,
    RecommendationTimeout,
    run_strategy_agent as run_real_strategy_agent,
)
```

권장 구조:

1. service wrapper는 backend 라우터가 의존하는 안정적인 import path로 유지합니다.
2. wrapper 내부에서 demo/mock flag를 확인합니다.
3. demo/mock flag가 명시적으로 켜진 경우에만 fixture를 반환합니다.
4. 기본값은 실제 Strategy Agent 호출입니다.

### 3.2 예외 매핑

`backend/app/api/recommend.py`에서 error code를 아래처럼 매핑합니다.

| 원인 | HTTP status | code | 비고 |
| --- | --- | --- | --- |
| 전체 Strategy timeout | 504 | `agent_timeout` | `asyncio.TimeoutError` 또는 `RecommendationTimeout` |
| LLM structured output/schema 실패 | 502 | `agent_failed` | `RecommendationFailed`, `StrategyLLMError` 계열 |
| Chroma/RAG 접근 실패 | 502 | `rag_unavailable` | Chroma 미설치, collection 없음, query 실패 |
| 예상하지 못한 내부 오류 | 500 | `agent_internal` | 로깅 후 generic message |

`_ERROR_MESSAGES`에는 `rag_unavailable`과 `agent_failed`를 추가합니다.

### 3.3 테스트 영향

현재 `backend/tests/test_recommend.py`는 fixture 기반 성공 응답을 전제로 합니다. 호출선 교체 후에는 다음 중 하나로 바꿉니다.

- 라우터 테스트: `app.services.strategy_invoker.run_strategy_agent`를 monkeypatch해 성공/timeout/schema/RAG 실패를 검증합니다.
- 통합 테스트: 임시 Chroma path와 최소 processed JSONL fixture를 빌드한 뒤 Strategy smoke를 별도로 검증합니다.

---

## 4. Chroma-backed RagService

### 4.1 파일 구조

권장 파일 구조:

```text
backend/app/rag/
  __init__.py
  service.py          # Protocol, 예외, factory
  chroma_service.py   # ChromaRagService
  filters.py          # patch family, where merge
```

`service.py`에는 인터페이스, `RagUnavailableError`, factory만 남기고, `InMemoryStubRagService`는 `backend/tests` fixture 또는 `backend/app/rag/testing.py`로 이동합니다.

### 4.2 검색 계약

`ChromaRagService`는 기존 `RagService` 계약을 유지합니다.

```python
def search(
    self,
    index: IndexName,
    query: str,
    *,
    k: int,
    patch_version: str,
    where: dict | None = None,
) -> list[RagChunk]: ...

def multi_search(
    self,
    plan: list[tuple[IndexName, str, int]],
    *,
    patch_version: str,
) -> list[RagChunk]: ...

def get_whitelist(self, patch_version: str) -> dict[str, set[str]]: ...
```

검색 규칙:

- patch family: `17.2` 요청 시 `17.2`, `17.2b`를 함께 조회합니다.
- fallback: `patch_version="all"`인 chunk는 모든 patch 검색에 포함합니다.
- where merge: 호출자가 넘긴 `where`와 patch filter를 모두 적용합니다.
- dedupe: 동일 `id`는 score가 높은 결과만 남깁니다.
- sort: score 내림차순으로 반환합니다.
- low-score filter: 기본 임계값은 `0.2`로 두고 settings에서 조정할 수 있게 합니다.
- empty collection: 예외가 아니라 빈 list를 반환하되, collection 접근 자체가 실패하면 `RagUnavailableError`를 발생시킵니다.

### 4.3 score 정규화

Chroma distance는 score와 방향이 다를 수 있습니다. `RagChunk.score`는 `0.0`부터 `1.0`까지의 유사도로 정규화합니다.

권장 변환:

```python
score = max(0.0, min(1.0, 1.0 - distance))
```

사용하는 Chroma metric이 바뀌면 변환 함수를 한 곳에서만 수정할 수 있게 둡니다.

### 4.4 whitelist 캐시

`get_whitelist()`는 `units`, `items`, `traits`, `augments` collection의 `metadata["name"]` 집합을 만듭니다.

캐시 정책:

- key: `patch_version`
- value: `{"units": set(...), "items": set(...), "traits": set(...), "augments": set(...)}`
- TTL: 5분
- max size: 16
- refresh: build/refresh CLI 실행 후 프로세스 재시작 또는 명시적 cache clear hook으로 갱신합니다.

현재 네 collection이 비어 있을 수 있으므로, 1차 구현에서는 빈 set을 정상 반환하고 `verify_grounding`이 과도하게 실패하지 않도록 테스트에서 기대값을 명확히 둡니다.

---

## 5. Strategy Agent와 RAG 주입

`rag_retrieve()`의 기본 인자가 import 시점의 `default_rag_service`에 고정되어 있습니다.

```python
async def rag_retrieve(
    state: StrategyState,
    *,
    rag: RagService = default_rag_service,
) -> dict:
```

전환 방법:

1. `get_rag_service()` factory를 둡니다.
2. `rag_retrieve()`의 기본 인자를 `rag: RagService | None = None`으로 바꿉니다.
3. 함수 내부에서 `active_rag = rag or get_rag_service()`를 평가합니다.
4. 테스트는 `rag` 인자를 직접 넘기거나 factory를 monkeypatch합니다.
5. LangGraph node 등록은 기존 함수명을 유지해 graph 영향 범위를 줄입니다.

이렇게 하면 runtime은 Chroma를 쓰고, 단위 테스트는 stub/fake를 주입할 수 있습니다.

---

## 6. RAG build CLI

### 6.1 CLI 경로와 명령

`backend/scripts/build_rag.py`를 추가합니다.

```bash
python -m backend.scripts.build_rag build --patch 17.2
python -m backend.scripts.build_rag refresh --index patch_summary --patch 17.2
python -m backend.scripts.build_rag whitelist --patch 17.2 --out whitelist.json
```

`python -m backend.scripts...` 실행을 안정적으로 만들려면 `backend/scripts/__init__.py`도 추가합니다.

### 6.2 build

`build`는 아래 순서로 동작합니다.

1. `data/rag/processed/*`에서 대상 patch의 JSONL을 찾습니다.
2. `deck_templates`는 `17.2` 요청 시 `17.2b`도 같은 family로 포함합니다.
3. JSONL 한 줄을 `RagChunk` 입력 형태로 정규화합니다.
4. `text`를 embedding하고 Chroma collection에 upsert합니다.
5. `current_patch.json`에 `current_patch`, `last_updated`, `fetched_at`, `record_count`, `sources`, `source_urls`, `jsonl_path`를 기록합니다.

### 6.3 refresh

`refresh`는 단일 index만 rebuild합니다.

```bash
python -m backend.scripts.build_rag refresh --index deck_templates --patch 17.2
```

정책:

- 기존 collection의 같은 patch family chunk를 삭제한 뒤 upsert합니다.
- 다른 patch와 `all` chunk는 유지합니다.
- 실패 시 manifest를 갱신하지 않습니다.

### 6.4 whitelist

`whitelist`는 Chroma 또는 processed JSONL에서 이름 집합을 export합니다.

```json
{
  "units": [],
  "items": [],
  "traits": [],
  "augments": []
}
```

1차 데이터에는 네 collection이 비어 있을 수 있습니다. 이 경우 빈 배열을 쓰고 경고를 stderr에 출력합니다.

---

## 7. RAG 데이터와 patch manifest 정리

### 7.1 1차 upsert 대상

이번 범위의 1차 upsert 대상은 현재 데이터가 있는 두 인덱스입니다.

| Index | 파일 | patch |
| --- | --- | --- |
| `patch_summary` | `data/rag/processed/patch_summary/17.2.jsonl` | `17.2` |
| `deck_templates` | `data/rag/processed/deck_templates/17.2b.jsonl` | `17.2b` |

### 7.2 후속 seed 대상

아래 인덱스는 최소 seed 또는 processed JSONL을 채우는 후속 작업으로 분리합니다.

- `units`
- `traits`
- `items`
- `augments`
- `playbook`
- `glossary`

다만 health와 whitelist는 빈 collection을 다룰 수 있어야 합니다.

### 7.3 patch version 정합성

settings 기본값과 RAG 데이터 기준을 맞춥니다.

- `backend/app/settings.py`: `patch_version = "17.2"`
- `backend/.env.example` 또는 문서화된 env 예시: `PATCH_VERSION=17.2`
- `current_patch.json`: `last_updated` 또는 `fetched_at` 필수

---

## 8. Public Interface 변경

### 8.1 `POST /api/recommend`

요청/응답 schema는 유지합니다.

보강할 error detail:

```json
{
  "code": "rag_unavailable",
  "message": "추천 근거 데이터를 불러오지 못했어요. 잠시 후 다시 시도해주세요.",
  "request_id": "..."
}
```

계약:

- `agent_timeout`: 504
- `agent_failed`: 502
- `rag_unavailable`: 502
- `agent_internal`: 500

### 8.2 `GET /api/health`

가능하면 processed JSONL count가 아니라 Chroma collection count를 반환합니다.

```json
{
  "status": "degraded",
  "patch_version": "17.2",
  "rag_chunks": {
    "units": 0,
    "traits": 0,
    "items": 0,
    "augments": 0,
    "deck_templates": 64,
    "playbook": 0,
    "patch_summary": 199,
    "glossary": 0
  },
  "uptime_s": 12
}
```

정책:

- Chroma path가 없으면 `degraded`
- 필수 collection 접근 실패 시 `degraded`
- 모든 collection이 존재하고 count가 1 이상이면 `ok`
- 이번 1차 데이터 범위에서는 일부 collection이 비어 있으므로 `degraded`가 정상일 수 있습니다.

### 8.3 `GET /api/patch-info`

`last_updated`가 manifest에서 정상 반환되도록 합니다.

우선순위:

1. `fetched_at`
2. `last_updated`
3. 없으면 `null`과 `data_may_be_insufficient_after_patch`

manifest 보강 후에는 정상 경로에서 `last_updated`가 ISO 8601 문자열이어야 합니다.

---

## 9. Live Research 유지 범위

현재 구현된 Live Research는 DuckDuckGo whitelist search와 `fetch_page` 중심입니다.

유지할 내용:

- `web_search`
- `fetch_page`
- domain whitelist
- robots.txt 확인
- 15초 timeout 시 `research_truncated` warning

이번 범위에서 제외할 내용:

- YouTube transcript tool
- YouTube transcript 의존성
- YouTube proxy 설정
- YouTube channel 기반 fact extraction

문서와 코드 주석에는 YouTube transcript가 MVP 제외이며, 프록시/네트워크 안정성 확인 전까지 비활성임을 명시합니다.

---

## 10. 구현 순서

### Phase 1. 추천 경로에서 mock 제거

1. `strategy_invoker.py`를 실제 Strategy API wrapper로 전환합니다.
2. demo/mock flag 경로를 명시적으로 분리합니다.
3. `/api/recommend` error mapping을 504/502/500으로 보강합니다.
4. 라우터 단위 테스트를 monkeypatch 기반으로 수정합니다.

완료 기준:

- `/api/recommend` 성공 테스트가 fixture 파일 직접 반환에 의존하지 않습니다.
- timeout/schema/RAG 실패 테스트가 각각 기대 status와 code를 검증합니다.

### Phase 2. Chroma-backed RAG Service 추가

1. `ChromaRagService`와 `RagUnavailableError`를 추가합니다.
2. patch family + `all` fallback 필터를 구현합니다.
3. score 정규화, dedupe, sorting, low-score filter를 구현합니다.
4. `get_whitelist()` TTL/LRU 캐시를 구현합니다.
5. `rag_retrieve()`가 factory 또는 명시 주입을 사용하게 바꿉니다.

완료 기준:

- 임시 Chroma path에서 `search`, `multi_search`, `get_whitelist` 단위 테스트가 통과합니다.
- 빈 collection은 빈 결과로 처리되고, 접근 실패는 `RagUnavailableError`로 분리됩니다.

### Phase 3. RAG build CLI 추가

1. `backend/scripts/build_rag.py`와 `backend/scripts/__init__.py`를 추가합니다.
2. `build`, `refresh`, `whitelist` subcommand를 구현합니다.
3. `patch_summary`, `deck_templates` JSONL upsert를 우선 지원합니다.
4. manifest에 timestamp와 source metadata를 기록합니다.

완료 기준:

- `python -m backend.scripts.build_rag build --patch 17.2`가 local Chroma를 생성합니다.
- `whitelist` 명령이 빈 whitelist라도 JSON 파일을 생성합니다.

### Phase 4. health와 patch-info 전환

1. `/api/health`를 Chroma collection count 기준으로 전환합니다.
2. Chroma 부재와 일부 collection empty를 `degraded`로 표현합니다.
3. `/api/patch-info`가 보강된 manifest timestamp를 반환하는지 검증합니다.

완료 기준:

- Chroma 없는 환경, 일부 collection만 있는 환경, 모든 collection이 있는 환경을 각각 테스트합니다.
- manifest timestamp가 있으면 `last_updated`가 `null`이 아닙니다.

### Phase 5. 통합 smoke

1. 임시 Chroma path에 최소 fixture를 build합니다.
2. LLM 호출은 monkeypatch하고 Strategy graph가 RAG chunk를 읽는지 검증합니다.
3. 로컬 서버에서 `/api/health`, `/api/patch-info`, `/api/recommend`를 smoke test합니다.

완료 기준:

- mock fixture 없이 Strategy Agent 진입점이 호출됩니다.
- 추천 응답의 deck/source/rationale이 RAG fixture에서 온 근거를 참조합니다.

---

## 11. Test Plan

### 11.1 Unit tests

- `ChromaRagService.search()`
  - patch family 필터
  - `all` fallback
  - score 내림차순
  - 동일 id 중복 제거
  - low-score filter
  - empty collection
- `ChromaRagService.multi_search()`
  - 여러 index/query plan 병합
  - 전체 결과 dedupe/sort
- `ChromaRagService.get_whitelist()`
  - `units`, `items`, `traits`, `augments` 이름 집합
  - 빈 collection
  - TTL/LRU 캐시 hit
- `/api/recommend`
  - 성공 시 Strategy wrapper 호출
  - timeout → 504 `agent_timeout`
  - schema/LLM 실패 → 502 `agent_failed`
  - RAG 접근 실패 → 502 `rag_unavailable`
  - unexpected error → 500 `agent_internal`

### 11.2 Integration tests

- 임시 Chroma path와 최소 JSONL fixture로 RAG build 후 search smoke를 실행합니다.
- `/api/recommend`가 mock fixture 없이 Strategy Agent 진입점을 호출하는지 검증합니다.
- `/api/health`가 Chroma collection 상태를 반영하는지 검증합니다.
- `/api/patch-info`가 manifest timestamp를 반영하는지 검증합니다.

### 11.3 Regression checks

```bash
cd backend
.venv/bin/python -m pytest tests -q
```

필요 시 frontend 계약 영향도 함께 확인합니다.

```bash
cd frontend
pnpm lint
pnpm typecheck
```

로컬 서버 smoke:

```bash
curl http://localhost:3000/api/health
curl http://localhost:3000/api/patch-info
curl -X POST http://localhost:3000/api/recommend \
  -H 'Content-Type: application/json' \
  -d '{"tier":"GOLD","play_style":"stable_top4","question":"현재 패치 추천 덱 알려줘"}'
```

---

## 12. 리스크와 대응

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| Chroma optional dependency가 설치되지 않음 | runtime에서 RAG 접근 실패 | `pip install -e ".[backend,dev,rag]"`를 backend setup 문서와 CI에 반영합니다. |
| Upstage API 키 없음 | 실제 LLM E2E 제한 | CI는 LLM monkeypatch + 실제 RAG fixture를 기본 검증으로 둡니다. |
| `units/items/traits/augments` 데이터 없음 | whitelist가 비어 grounding 검증이 보수적으로 동작할 수 있음 | 1차 구현에서는 빈 whitelist를 허용하고, 최소 seed 보강을 후속 작업으로 둡니다. |
| patch version source가 둘로 갈라짐 | UI와 RAG 검색 기준 불일치 | `PATCH_VERSION=17.2`와 manifest `current_patch`를 함께 갱신합니다. |
| Live Research 네트워크 변동 | 추천 latency와 근거 품질 변동 | timeout과 `research_truncated` warning을 유지하고, YouTube transcript는 이번 범위에서 제외합니다. |

---

## 13. 완료 정의

이 계획의 1차 완료 조건은 다음과 같습니다.

- `/api/recommend` 기본 경로가 mock fixture를 반환하지 않습니다.
- Strategy Agent가 Chroma-backed RAG 결과를 읽어 추천 생성 context로 사용합니다.
- RAG build CLI로 현재 repo의 `patch_summary`, `deck_templates` 데이터를 Chroma에 재생성할 수 있습니다.
- `/api/health`와 `/api/patch-info`가 실제 Chroma/manifest 상태를 반영합니다.
- backend unit/integration test가 mock fixture 제거 이후의 성공/실패 계약을 검증합니다.
- YouTube transcript는 코드와 문서 어디에서도 MVP 필수 경로로 취급하지 않습니다.
