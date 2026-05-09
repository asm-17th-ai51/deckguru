import time
from pathlib import Path

from fastapi import APIRouter

from app.settings import settings

router = APIRouter()

_startup_time = time.time()

_RAG_INDICES = [
    "units", "traits", "items", "augments",
    "deck_templates", "playbook", "patch_summary", "glossary",
]


def _count_rag_chunks() -> dict[str, int]:
    counts: dict[str, int] = {}
    processed_dir = Path(settings.chroma_path).parent.parent / "processed"
    for index in _RAG_INDICES:
        index_dir = processed_dir / index
        total = 0
        if index_dir.exists():
            for jsonl_file in index_dir.glob("*.jsonl"):
                try:
                    total += sum(1 for line in jsonl_file.read_text(encoding="utf-8").splitlines() if line.strip())
                except Exception:
                    pass
        counts[index] = total
    return counts


@router.get(
    "/health",
    summary="서버 상태 확인",
    description="""
서버와 RAG 인덱스의 현재 상태를 반환합니다.

- `status`: RAG 인덱스 중 하나라도 비어 있으면 `degraded`, 모두 정상이면 `ok`
- `rag_chunks`: 8개 인덱스(units, traits, items, augments, deck_templates, playbook, patch_summary, glossary)별 chunk 수
- `uptime_s`: 서버 기동 후 경과 시간(초)
""",
)
async def health():
    rag_chunks = _count_rag_chunks()
    status = "degraded" if any(v == 0 for v in rag_chunks.values()) else "ok"
    return {
        "status": status,
        "patch_version": settings.patch_version,
        "rag_chunks": rag_chunks,
        "uptime_s": int(time.time() - _startup_time),
    }
