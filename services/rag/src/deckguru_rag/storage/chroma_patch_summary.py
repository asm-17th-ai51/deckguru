import json
from pathlib import Path
from typing import Any

from deckguru_rag.embeddings import BGEM3Embedding


INDEX_NAMES = ["patch_summary", "deck_templates", "units", "items", "traits", "augments", "playbook"]


def build_chroma_indices(
    *,
    data_dir: Path,
    persist_dir: Path,
    patch_version: str | None = None,
) -> dict[str, int]:
    chromadb = _import_chromadb()
    persist_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(persist_dir))
    embedder = BGEM3Embedding()

    counts: dict[str, int] = {}
    base_processed_dir = data_dir.parent
    for index_name in INDEX_NAMES:
        index_dir = data_dir if index_name == "patch_summary" else base_processed_dir / index_name
        current_patch = patch_version or _read_current_patch(index_dir)
        records = _load_jsonl(index_dir / f"{current_patch}.jsonl")
        _recreate_collection(client, index_name)
        collection = client.get_collection(name=index_name)
        documents = [record["text"] for record in records]
        collection.upsert(
            ids=[record["id"] for record in records],
            documents=documents,
            metadatas=[_metadata(record, index_name) for record in records],
            embeddings=embedder.embed_many(documents),
        )
        counts[index_name] = len(records)
    return counts


def build_patch_summary_chroma(
    *,
    data_dir: Path,
    persist_dir: Path,
    patch_version: str | None = None,
) -> dict[str, int]:
    return build_chroma_indices(
        data_dir=data_dir,
        persist_dir=persist_dir,
        patch_version=patch_version,
    )


def _read_current_patch(data_dir: Path) -> str:
    manifest = json.loads((data_dir / "current_patch.json").read_text(encoding="utf-8"))
    return str(manifest["current_patch"])


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _recreate_collection(client: Any, name: str) -> None:
    try:
        client.delete_collection(name=name)
    except Exception:
        pass
    client.create_collection(name=name)


def _metadata(record: dict[str, Any], index_name: str) -> dict[str, str | int | float | bool]:
    return {
        "index": index_name,
        "patch_version": str(record.get("patch_version") or ""),
        "source": str(record.get("source") or ""),
        "source_url": str(record.get("source_url") or ""),
        "source_title": str(record.get("source_title") or ""),
        "section": str(record.get("section") or ""),
        "name": str(record.get("name") or ""),
        "cost": _metadata_scalar(record.get("cost")),
        "traits": _metadata_list(record.get("traits")),
        "role": str(record.get("role") or ""),
        "skill_name": str(record.get("skill_name") or ""),
        "image_url": str(record.get("image_url") or ""),
        "recipe": str(record.get("recipe") or ""),
        "effect": str(record.get("effect") or ""),
        "tags": _metadata_list(record.get("tags")),
        "tiers": _metadata_list(record.get("tiers")),
        "champions": _metadata_list(record.get("champions")),
        "tier": str(record.get("tier") or ""),
        "topic": str(record.get("topic") or ""),
        "phase": str(record.get("phase") or ""),
        "title": str(record.get("title") or ""),
        "term": str(record.get("term") or ""),
        "target_kind": str(record.get("target_kind") or "unknown"),
        "target_name": str(record.get("target_name") or ""),
        "change_type": str(record.get("change_type") or "unknown"),
    }


def _metadata_scalar(value: Any) -> str | int | float | bool:
    if isinstance(value, (str, int, float, bool)):
        return value
    return ""


def _metadata_list(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item)
    return str(value or "")


def _import_chromadb() -> Any:
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError(
            "chromadb is not installed. Install RAG dependencies with "
            "`pip install -r services/rag/requirements.txt`."
        ) from exc
    return chromadb
