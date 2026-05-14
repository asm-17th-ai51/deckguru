import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "services" / "rag" / "src"
sys.path.insert(0, str(SRC_ROOT))

from deckguru_rag.processing import build_lolchess_traits_jsonl  # noqa: E402


def main() -> None:
    raw_dir = REPO_ROOT / "data" / "rag" / "raw" / "lolchess"
    output_dir = REPO_ROOT / "data" / "rag" / "processed" / "traits"
    output_path = build_lolchess_traits_jsonl(
        raw_dir,
        output_dir,
        patch_version=_current_patch(),
    )
    print(output_path.relative_to(REPO_ROOT))


def _current_patch() -> str:
    manifest_path = REPO_ROOT / "data" / "rag" / "processed" / "patch_summary" / "current_patch.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return str(manifest["current_patch"])


if __name__ == "__main__":
    main()
