# 덱구루(DeckGuru) — Spec 문서

51조 프로젝트 "롤토체스(TFT) 메타 분석 및 덱 추천 Agentic AI 서비스"의 AI native 개발용 사양 문서 집합.

## 핵심 원칙

1. **Grounding-First**: 응답에 등장하는 모든 고유명사(기물·아이템·특성·증강체)는 RAG 화이트리스트에 존재해야 한다. 미존재 = 응답에서 제거.
2. **Patch-Versioned**: 모든 데이터 chunk와 응답은 `patch_version`을 1급 메타데이터로 갖는다. 옛 패치 정보가 현재 응답에 섞이지 않는다.
3. **결정성(Determinism)**: 동일 입력 → 동일 응답. LLM은 `temperature=0`, structured output, schema 검증.
4. **Source-Mandatory**: 외부 출처에서 인용한 모든 사실은 `sources[]` 와 1:1 대응. 출처 없는 사실은 confidence 강등.
5. **Schema-First**: 모든 인터페이스는 `07-data-contracts.md`의 schema가 단일 진실 소스. 머지 후에 구현.

## 읽는 순서

| 순서 | 문서 | 대상 |
|---|---|---|
| 1 | [00-overview.md](./00-overview.md) | 전원 (필독) |
| 2 | [01-architecture.md](./01-architecture.md) | 전원 |
| 3 | [07-data-contracts.md](./07-data-contracts.md) | 전원 (필독) |
| 4 | [08-roles-and-handoffs.md](./08-roles-and-handoffs.md) | 전원 (필독) |
| 5 | [02-agent-strategy-spec.md](./02-agent-strategy-spec.md) | Agent (Strategy/Orchestration) 담당 |
| 6 | [03-agent-rag-spec.md](./03-agent-rag-spec.md) | Agent (RAG/Data) 담당 |
| 7 | [04-agent-research-spec.md](./04-agent-research-spec.md) | Agent (Live Research/Tools) 담당 |
| 8 | [05-backend-spec.md](./05-backend-spec.md) | Backend 담당 |
| 9 | [06-frontend-spec.md](./06-frontend-spec.md) | Frontend 담당 |

## 팀 구성 (5인)

- AI/Agent: 3명 (Strategy / RAG / Research)
- Backend: 1명
- Frontend: 1명

## 참고

원본 기획서는 상위 디렉토리의 `[51조]프로젝트 기획서 양식_51조_롤토체스 메타 분석 및 덱 추천 AI 서비스.docx.pdf` 참조. 본 spec은 기획서를 그대로 옮기지 않고, 모순/누락/현실성 부족을 보정했다. 각 문서 끝에 **§기획서 피드백** 섹션이 있다.
