from __future__ import annotations

from pathlib import Path

from backend.scripts import build_rag


def test_supported_build_indices_include_processed_rag_sources():
    assert set(build_rag.SUPPORTED_BUILD_INDICES) == {
        "patch_summary",
        "deck_templates",
        "units",
        "items",
        "traits",
        "augments",
        "playbook",
    }


def test_jsonl_paths_for_patch_falls_back_to_all_jsonl(monkeypatch, tmp_path):
    processed_dir = tmp_path / "processed"
    playbook_dir = processed_dir / "playbook"
    playbook_dir.mkdir(parents=True)
    all_path = playbook_dir / "all.jsonl"
    all_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(build_rag, "_processed_dir", lambda: processed_dir)

    assert build_rag._jsonl_paths_for_patch("playbook", "17.2") == [all_path]


def test_jsonl_paths_for_patch_prefers_patch_family_files(monkeypatch, tmp_path):
    processed_dir = tmp_path / "processed"
    traits_dir = processed_dir / "traits"
    traits_dir.mkdir(parents=True)
    patch_path = traits_dir / "17.2.jsonl"
    patch_b_path = traits_dir / "17.2b.jsonl"
    all_path = traits_dir / "all.jsonl"
    other_path = traits_dir / "17.3.jsonl"
    for path in (patch_path, patch_b_path, all_path, other_path):
        path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(build_rag, "_processed_dir", lambda: processed_dir)

    assert build_rag._jsonl_paths_for_patch("traits", "17.2") == [
        patch_path,
        patch_b_path,
    ]
