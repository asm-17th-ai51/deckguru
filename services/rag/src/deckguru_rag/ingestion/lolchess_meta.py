import html
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal
from urllib.request import Request, urlopen


LOLCHESS_META_URL = "https://lolchess.gg/meta?hl=ko"
LOLCHESS_DECKS_URL = "https://lolchess.gg/decks?hl=ko"
LOLCHESS_CHAMPIONS_URL = "https://lolchess.gg/champions/set17?hl=ko"
LOLCHESS_ITEMS_URL = "https://lolchess.gg/items/set17?hl=ko"
LOLCHESS_TRAITS_URL = "https://lolchess.gg/synergies/set17?hl=ko"
LOLCHESS_AUGMENTS_URL = "https://lolchess.gg/augments/set17?hl=ko"
LOLCHESS_PLAYBOOK_URLS = {
    "role": "https://lolchess.gg/guide/role?hl=ko",
    "reroll": "https://lolchess.gg/guide/reroll?hl=ko",
    "rounds": "https://lolchess.gg/guide/rounds?hl=ko",
    "exp": "https://lolchess.gg/guide/exp?hl=ko",
    "damage": "https://lolchess.gg/guide/damage?hl=ko",
    "hotkeys": "https://lolchess.gg/guide/hotkeys?hl=ko",
}

LolchessMetaSource = Literal[
    "meta",
    "decks",
    "champions",
    "items",
    "traits",
    "augments",
    "playbook_role",
    "playbook_reroll",
    "playbook_rounds",
    "playbook_exp",
    "playbook_damage",
    "playbook_hotkeys",
]


@dataclass(frozen=True)
class LolchessPageDocument:
    source: LolchessMetaSource
    url: str
    fetched_at: str
    next_data: dict[str, Any]
    page_text: str = ""

    @classmethod
    def create(
        cls,
        *,
        source: LolchessMetaSource,
        url: str,
        next_data: dict[str, Any],
        page_text: str = "",
    ) -> "LolchessPageDocument":
        return cls(
            source=source,
            url=url,
            fetched_at=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            next_data=next_data,
            page_text=page_text,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fetch_lolchess_meta_pages(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    documents = [
        _fetch_page(source="meta", url=LOLCHESS_META_URL),
        _fetch_page(source="decks", url=LOLCHESS_DECKS_URL),
    ]

    written: list[Path] = []
    for document in documents:
        path = output_dir / f"lolchess_{document.source}.json"
        path.write_text(
            json.dumps(document.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(path)
    return written


def fetch_lolchess_champions_page(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    document = _fetch_page(source="champions", url=LOLCHESS_CHAMPIONS_URL)
    path = output_dir / "lolchess_champions.json"
    path.write_text(
        json.dumps(document.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def fetch_lolchess_items_page(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    document = _fetch_page(source="items", url=LOLCHESS_ITEMS_URL)
    path = output_dir / "lolchess_items.json"
    path.write_text(
        json.dumps(document.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def fetch_lolchess_traits_page(output_dir: Path) -> Path:
    return _fetch_single_to_path(output_dir, source="traits", url=LOLCHESS_TRAITS_URL)


def fetch_lolchess_augments_page(output_dir: Path) -> Path:
    return _fetch_single_to_path(output_dir, source="augments", url=LOLCHESS_AUGMENTS_URL)


def fetch_lolchess_playbook_pages(output_dir: Path) -> list[Path]:
    written: list[Path] = []
    for topic, url in LOLCHESS_PLAYBOOK_URLS.items():
        source = f"playbook_{topic}"
        written.append(_fetch_single_to_path(output_dir, source=source, url=url))
    return written


def _fetch_single_to_path(output_dir: Path, *, source: LolchessMetaSource, url: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    document = _fetch_page(source=source, url=url)
    path = output_dir / f"lolchess_{source}.json"
    path.write_text(
        json.dumps(document.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def _fetch_page(*, source: LolchessMetaSource, url: str) -> LolchessPageDocument:
    raw_html = _fetch_text(url)
    next_data = _extract_next_data(raw_html)
    page_text = _extract_page_text(raw_html)
    return LolchessPageDocument.create(
        source=source,
        url=url,
        next_data=next_data,
        page_text=page_text,
    )


def _fetch_text(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "DeckGuruRAG/0.1 (+https://github.com/asm-17th-ai51/deckguru)",
            "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        },
    )
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _extract_next_data(raw_html: str) -> dict[str, Any]:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        raw_html,
    )
    if not match:
        raise ValueError("Could not find __NEXT_DATA__ script in Lolchess page.")
    return json.loads(html.unescape(match.group(1)))


def _extract_page_text(raw_html: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw_html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()
