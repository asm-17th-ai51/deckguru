"""RAG Service interface.

소유: Agent-2 (03-agent-rag-spec.md).
호출자: Agent-1 (Strategy), Agent-3 (Research).

본 파일의 `RagService` Protocol이 인터페이스 계약(08-roles-and-handoffs §2.2).
Agent-2가 ChromaDB-backed 구현으로 교체할 때까지 `InMemoryStubRagService`를
fallback으로 사용 — Strategy Agent를 단독으로 돌려보고 prompt 튜닝하기 위함.
"""

from __future__ import annotations

from typing import Protocol

from app.schemas.shared import IndexName, RagChunk


class RagService(Protocol):
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

    def get_whitelist(self, patch_version: str) -> dict[str, set[str]]:
        """patch_version의 화이트리스트.

        Returns:
            {"units": {...}, "items": {...}, "traits": {...}, "augments": {...}}
        """
        ...


# ---------------------------------------------------------------------------
# Stub — Agent-2 구현이 들어오기 전 Strategy Agent를 단독 실행할 때 사용.
# ---------------------------------------------------------------------------


class InMemoryStubRagService:
    """소량의 하드코딩된 데이터로 Strategy Agent 단독 검증 가능.

    실제 검색 품질은 보장하지 않음. Agent-2 구현 머지 후 제거 또는 테스트 전용으로 강등.
    """

    def __init__(self) -> None:
        self._whitelist: dict[str, set[str]] = {
            "units": {
                "정밀의 사도", "기계 학자", "사이버시티 챔피언",
                "어둠의 화신", "9코스트 정밀", "광신도",
                "라이트브링어", "강철의 수호자", "드림리프 마법사",
            },
            "items": {
                "구인수의 격노검", "거인 학살자", "최후의 속삭임",
                "푸른 파수꾼", "정의의 손", "굳건한 심장",
                "용의 발톱", "자드자의 심장", "곡궁",
                "BF대검", "쇠사슬 조끼",
            },
            "traits": {"정밀", "기계 학자", "사이버시티", "어둠", "광신도"},
            "augments": {"내일의 정밀", "광신도의 광기", "리롤의 정석"},
        }

        self._chunks: dict[IndexName, list[RagChunk]] = {
            "units": [
                RagChunk(
                    id="u_jeongmil_14.9",
                    index="units",
                    text="정밀의 사도: 4코스트 DPS, 정밀 시너지 핵심.",
                    metadata={"name": "정밀의 사도", "cost": 4, "patch_version": "14.9"},
                    score=0.85,
                ),
                RagChunk(
                    id="u_gigye_14.9",
                    index="units",
                    text="기계 학자: 3코스트 캐스터, 마나 시너지.",
                    metadata={"name": "기계 학자", "cost": 3, "patch_version": "14.9"},
                    score=0.78,
                ),
            ],
            "items": [
                RagChunk(
                    id="i_guinsu_14.9",
                    index="items",
                    text="구인수의 격노검: AD 캐리에 핵심.",
                    metadata={"name": "구인수의 격노검", "patch_version": "14.9"},
                    score=0.82,
                ),
            ],
            "deck_templates": [
                RagChunk(
                    id="d_jeongmil_reroll_14.9",
                    index="deck_templates",
                    text=(
                        "정밀 리롤 덱: 정밀의 사도를 메인 캐리로, "
                        "기계 학자 + 광신도 시너지. 초중반 안정적, 8레벨 도달 후 9코 보강."
                    ),
                    metadata={
                        "name": "정밀 리롤",
                        "core_units": ["정밀의 사도", "기계 학자", "광신도", "라이트브링어"],
                        "key_items": ["구인수의 격노검", "최후의 속삭임", "정의의 손"],
                        "difficulty": "easy",
                        "preferred_styles": ["stable_top4", "easy_beginner"],
                        "patch_version": "14.9",
                    },
                    score=0.88,
                ),
                RagChunk(
                    id="d_cyber_14.9",
                    index="deck_templates",
                    text=(
                        "사이버시티 9코 덱: 사이버시티 챔피언 6단계 + 9코스트 정밀. "
                        "고점 1등형, 어그로 운영."
                    ),
                    metadata={
                        "name": "사이버시티 9코",
                        "core_units": ["사이버시티 챔피언", "9코스트 정밀", "어둠의 화신"],
                        "key_items": ["구인수의 격노검", "거인 학살자", "최후의 속삭임"],
                        "difficulty": "hard",
                        "preferred_styles": ["high_risk_first"],
                        "patch_version": "14.9",
                    },
                    score=0.81,
                ),
            ],
            "playbook": [
                RagChunk(
                    id="pb_economy_early",
                    index="playbook",
                    text="2-1 50골드 경제 빌드, 3-2 4레벨 도달 후 안정화.",
                    metadata={"topic": "economy", "phase": "early"},
                    score=0.7,
                ),
            ],
            "patch_summary": [
                RagChunk(
                    id="ps_14.9_1",
                    index="patch_summary",
                    text="14.9 패치: 정밀 시너지 버프, 사이버시티 챔피언 너프.",
                    metadata={
                        "patch_version": "14.9",
                        "change_type": "buff",
                        "target_kind": "trait",
                        "target_name": "정밀",
                    },
                    score=0.9,
                ),
            ],
            "traits": [],
            "augments": [],
            "glossary": [],
        }

    def search(
        self,
        index: IndexName,
        query: str,
        *,
        k: int,
        patch_version: str,
        where: dict | None = None,
    ) -> list[RagChunk]:
        chunks = [
            c for c in self._chunks.get(index, [])
            if c.metadata.get("patch_version", patch_version) == patch_version
        ]
        return chunks[:k]

    def multi_search(
        self,
        plan: list[tuple[IndexName, str, int]],
        *,
        patch_version: str,
    ) -> list[RagChunk]:
        out: list[RagChunk] = []
        for index, query, k in plan:
            out.extend(self.search(index, query, k=k, patch_version=patch_version))
        return out

    def get_whitelist(self, patch_version: str) -> dict[str, set[str]]:
        return {k: set(v) for k, v in self._whitelist.items()}


# 기본 인스턴스 — Strategy Agent가 fallback 으로 import.
# Agent-2 구현 후에는 backend/app/services에서 ChromaRagService를 의존성 주입.
default_rag_service: RagService = InMemoryStubRagService()
