import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class DeckTemplateRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    name: str
    core_units: list[str]
    key_items: list[str]
    traits: list[str]
    average_place: float | None
    win_rate: float | None
    top4_rate: float | None
    play_rate: float | None
    games: int | None
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class UnitRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    key: str
    ingame_key: str
    name: str
    cost: int
    traits: list[str]
    role: str
    image_url: str | None
    skill_name: str | None
    skill_desc: str | None
    attack_range: int | None
    attack_speed: float | None
    armor: int | None
    magical_resistance: int | None
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ItemRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    key: str
    name: str
    recipe: str
    effect: str
    tags: list[str]
    recommended_for_units: list[str]
    image_url: str | None
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class TraitRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    key: str
    ingame_key: str
    name: str
    tiers: list[int]
    synergy_summary: str
    champions: list[str]
    image_url: str | None
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class AugmentRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    key: str
    ingame_key: str
    name: str
    tier: str
    effect: str
    synergy_decks: list[str]
    image_url: str | None
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class PlaybookRecord:
    id: str
    index: str
    patch_version: str
    source: str
    source_url: str
    fetched_at: str
    topic: str
    phase: str
    title: str
    text: str
    metadata: dict[str, Any]


def build_lolchess_meta_jsonl(raw_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[DeckTemplateRecord] = []

    for raw_path in sorted(raw_dir.glob("lolchess_*.json")):
        document = json.loads(raw_path.read_text(encoding="utf-8"))
        records.extend(_records_from_document(document))

    records = _dedupe_records(records)
    patch_version = _select_patch_version(records)
    output_path = output_dir / f"{patch_version}.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_manifest(output_dir, patch_version, records)
    return output_path


def build_lolchess_augments_jsonl(raw_dir: Path, output_dir: Path, *, patch_version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "lolchess_augments.json"
    document = json.loads(raw_path.read_text(encoding="utf-8"))
    records = _augment_records_from_document(document, patch_version=patch_version)

    output_path = output_dir / f"{patch_version}.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_augments_manifest(output_dir, patch_version, records)
    return output_path


def build_lolchess_items_jsonl(raw_dir: Path, output_dir: Path, *, patch_version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "lolchess_items.json"
    document = json.loads(raw_path.read_text(encoding="utf-8"))
    records = _item_records_from_document(document, patch_version=patch_version)

    output_path = output_dir / f"{patch_version}.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_items_manifest(output_dir, patch_version, records)
    return output_path


def build_lolchess_playbook_jsonl(raw_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[PlaybookRecord] = []
    for raw_path in sorted(raw_dir.glob("lolchess_playbook_*.json")):
        document = json.loads(raw_path.read_text(encoding="utf-8"))
        records.append(_playbook_record_from_document(document))

    output_path = output_dir / "all.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_playbook_manifest(output_dir, records)
    return output_path


def build_lolchess_traits_jsonl(raw_dir: Path, output_dir: Path, *, patch_version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "lolchess_traits.json"
    document = json.loads(raw_path.read_text(encoding="utf-8"))
    champion_lookup = _trait_champion_lookup(raw_dir)
    records = _trait_records_from_document(
        document,
        patch_version=patch_version,
        champion_lookup=champion_lookup,
    )

    output_path = output_dir / f"{patch_version}.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_traits_manifest(output_dir, patch_version, records)
    return output_path


def build_lolchess_units_jsonl(raw_dir: Path, output_dir: Path, *, patch_version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / "lolchess_champions.json"
    document = json.loads(raw_path.read_text(encoding="utf-8"))
    records = _unit_records_from_document(document, patch_version=patch_version)

    output_path = output_dir / f"{patch_version}.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for record in records:
            file.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    _write_units_manifest(output_dir, patch_version, records)
    return output_path


def _augment_records_from_document(document: dict[str, Any], *, patch_version: str) -> list[AugmentRecord]:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    augments = _dedupe_augments(_find_augment_records(document["next_data"]))
    return [
        _augment_record_from_augment(augment, source, source_url, fetched_at, patch_version)
        for augment in augments
        if _is_public_augment(augment)
    ]


def _find_augment_records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        augments = value.get("augments")
        if isinstance(augments, list):
            records.extend(augment for augment in augments if isinstance(augment, dict))
        for child in value.values():
            records.extend(_find_augment_records(child))
    elif isinstance(value, list):
        for item in value:
            records.extend(_find_augment_records(item))
    return records


def _dedupe_augments(augments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for augment in augments:
        key = _first_string(augment, ["ingameKey", "key", "apiName", "id"])
        if key:
            deduped[key] = augment
    return sorted(deduped.values(), key=lambda augment: (int(augment.get("tier") or 0), str(augment.get("key") or "")))


def _is_public_augment(augment: dict[str, Any]) -> bool:
    if bool(augment.get("isHidden")):
        return False
    try:
        tier = int(augment.get("tier"))
    except (TypeError, ValueError):
        return False
    if tier not in {1, 2, 3}:
        return False
    name = augment.get("name")
    effect = augment.get("desc")
    return isinstance(name, str) and bool(name.strip()) and isinstance(effect, str) and bool(effect.strip())


def _augment_record_from_augment(
    augment: dict[str, Any],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
) -> AugmentRecord:
    key = _first_string(augment, ["key", "apiName", "id"]) or "unknown"
    ingame_key = _first_string(augment, ["ingameKey"]) or key
    name = _first_string(augment, ["name"]) or key
    effect = _clean_text(_first_string(augment, ["desc", "effect", "description"]) or "")
    tier = _augment_tier_name(augment.get("tier"))
    text = _build_augment_text(name=name, tier=tier, effect=effect)
    return AugmentRecord(
        id=_augment_record_id(patch_version, ingame_key),
        index="augments",
        patch_version=patch_version,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        key=key,
        ingame_key=ingame_key,
        name=name,
        tier=tier,
        effect=effect,
        synergy_decks=[],
        image_url=_first_string(augment, ["imageUrl", "iconUrl"]),
        text=text,
        metadata={"raw_key": key, "tags": augment.get("tags") or []},
    )


def _playbook_record_from_document(document: dict[str, Any]) -> PlaybookRecord:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    topic = source.replace("playbook_", "")
    page_text = str(document.get("page_text") or "")
    title = _playbook_title(topic)
    cleaned = _clean_playbook_text(page_text, title)
    return PlaybookRecord(
        id=_playbook_record_id(topic),
        index="playbook",
        patch_version="all",
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        topic=topic,
        phase=_playbook_phase(topic),
        title=title,
        text=cleaned,
        metadata={"raw_source": source},
    )


def _trait_records_from_document(
    document: dict[str, Any],
    *,
    patch_version: str,
    champion_lookup: dict[str, list[str]],
) -> list[TraitRecord]:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    traits = _dedupe_traits(_find_trait_records(document["next_data"]))
    return [
        _trait_record_from_trait(trait, source, source_url, fetched_at, patch_version, champion_lookup)
        for trait in traits
        if _is_public_trait(trait)
    ]


def _find_trait_records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        traits = value.get("traits")
        if isinstance(traits, list):
            records.extend(trait for trait in traits if isinstance(trait, dict))
        for child in value.values():
            records.extend(_find_trait_records(child))
    elif isinstance(value, list):
        for item in value:
            records.extend(_find_trait_records(item))
    return records


def _dedupe_traits(traits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for trait in traits:
        key = _first_string(trait, ["ingameKey", "key", "apiName", "id"])
        if key:
            deduped[key] = trait
    return sorted(deduped.values(), key=lambda trait: (str(trait.get("type") or ""), str(trait.get("key") or "")))


def _is_public_trait(trait: dict[str, Any]) -> bool:
    name = trait.get("name")
    return isinstance(name, str) and bool(name.strip())


def _trait_record_from_trait(
    trait: dict[str, Any],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
    champion_lookup: dict[str, list[str]],
) -> TraitRecord:
    key = _first_string(trait, ["key", "apiName", "id"]) or "unknown"
    ingame_key = _first_string(trait, ["ingameKey"]) or key
    name = _first_string(trait, ["name"]) or key
    tiers = _trait_tiers(trait)
    summary = _trait_summary(trait)
    champions = champion_lookup.get(key, []) + champion_lookup.get(ingame_key, [])
    champions = _dedupe_strings(champions)
    text = _build_trait_text(name=name, tiers=tiers, summary=summary, champions=champions)
    return TraitRecord(
        id=_trait_record_id(patch_version, ingame_key),
        index="traits",
        patch_version=patch_version,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        key=key,
        ingame_key=ingame_key,
        name=name,
        tiers=tiers,
        synergy_summary=summary,
        champions=champions,
        image_url=_first_string(trait, ["imageUrl", "blackImageUrl", "whiteImageUrl"]),
        text=text,
        metadata={"raw_key": key, "type": str(trait.get("type") or "")},
    )


def _item_records_from_document(document: dict[str, Any], *, patch_version: str) -> list[ItemRecord]:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    items = _dedupe_items(_find_item_records(document["next_data"]))
    return [
        _item_record_from_item(item, source, source_url, fetched_at, patch_version)
        for item in items
        if _is_public_item(item)
    ]


def _find_item_records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        items = value.get("items")
        if isinstance(items, list):
            records.extend(item for item in items if isinstance(item, dict))
        for child in value.values():
            records.extend(_find_item_records(child))
    elif isinstance(value, list):
        for item in value:
            records.extend(_find_item_records(item))
    return records


def _dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        key = _first_string(item, ["key", "apiName", "id"])
        if key:
            deduped[key] = item
    return sorted(deduped.values(), key=lambda item: str(item.get("key") or ""))


def _is_public_item(item: dict[str, Any]) -> bool:
    if any(bool(item.get(key)) for key in ("isHidden", "isDisabled")):
        return False
    name = item.get("name")
    return isinstance(name, str) and bool(name.strip())


def _item_record_from_item(
    item: dict[str, Any],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
) -> ItemRecord:
    key = _first_string(item, ["key", "apiName", "id"]) or "unknown"
    name = _first_string(item, ["name"]) or key
    recipe = _item_recipe(item)
    effect = _clean_text(_first_string(item, ["desc", "effect", "description"]) or "")
    tags = _item_tags(item, effect)
    text = _build_item_text(name=name, recipe=recipe, effect=effect, tags=tags)
    return ItemRecord(
        id=_item_record_id(patch_version, key),
        index="items",
        patch_version=patch_version,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        key=key,
        name=name,
        recipe=recipe,
        effect=effect,
        tags=tags,
        recommended_for_units=[],
        image_url=_first_string(item, ["imageUrl", "iconUrl"]),
        text=text,
        metadata={
            "raw_key": key,
            "is_trait": bool(item.get("isTrait")),
            "is_new": bool(item.get("isNew")),
        },
    )


def _unit_records_from_document(document: dict[str, Any], *, patch_version: str) -> list[UnitRecord]:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    champions = _dedupe_champions(_find_champion_records(document["next_data"]))
    return [
        _unit_record_from_champion(champion, source, source_url, fetched_at, patch_version)
        for champion in champions
        if _is_public_champion(champion)
    ]


def _find_champion_records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if isinstance(value, dict):
        champions = value.get("champions")
        if isinstance(champions, list):
            records.extend(champion for champion in champions if isinstance(champion, dict))
        for child in value.values():
            records.extend(_find_champion_records(child))
    elif isinstance(value, list):
        for item in value:
            records.extend(_find_champion_records(item))
    return records


def _dedupe_champions(champions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for champion in champions:
        key = _first_string(champion, ["ingameKey", "key"])
        if key:
            deduped[key] = champion
    return sorted(deduped.values(), key=lambda champion: (_unit_cost(champion), str(champion.get("key") or "")))


def _is_public_champion(champion: dict[str, Any]) -> bool:
    if any(bool(champion.get(key)) for key in ("isHidden", "isHiddenGuide", "isHiddenLanding", "isHiddenTeamBuilder")):
        return False
    if _unit_cost(champion) <= 0:
        return False
    name = champion.get("name")
    return isinstance(name, str) and bool(name.strip())


def _unit_record_from_champion(
    champion: dict[str, Any],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
) -> UnitRecord:
    key = _first_string(champion, ["key"]) or "unknown"
    ingame_key = _first_string(champion, ["ingameKey"]) or key
    name = _first_string(champion, ["name"]) or key
    traits = _dedupe_strings([trait for trait in champion.get("traits", []) if isinstance(trait, str)])
    role = _normalise_role(_first_string(champion, ["role"]), champion)
    skill = champion.get("skill") if isinstance(champion.get("skill"), dict) else {}
    skill_name = _first_string(skill, ["name"])
    skill_desc = _clean_text(_first_string(skill, ["desc"]) or "")
    text = _build_unit_text(
        name=name,
        cost=_unit_cost(champion),
        traits=traits,
        role=role,
        skill_name=skill_name,
        skill_desc=skill_desc,
    )
    return UnitRecord(
        id=_unit_record_id(patch_version, ingame_key),
        index="units",
        patch_version=patch_version,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        key=key,
        ingame_key=ingame_key,
        name=name,
        cost=_unit_cost(champion),
        traits=traits,
        role=role,
        image_url=_first_string(champion, ["imageUrl", "originalImageUrl"]),
        skill_name=skill_name,
        skill_desc=skill_desc,
        attack_range=_first_int(champion, ["attackRange"]),
        attack_speed=_first_float(champion, ["attackSpeed"]),
        armor=_first_int(champion, ["armor"]),
        magical_resistance=_first_int(champion, ["magicalResistance"]),
        text=text,
        metadata={"raw_key": key, "raw_role": str(champion.get("role") or "")},
    )


def _records_from_document(document: dict[str, Any]) -> list[DeckTemplateRecord]:
    source = str(document["source"])
    source_url = str(document["url"])
    fetched_at = str(document["fetched_at"])
    queries = _queries(document["next_data"])
    refs = _collect_refs(queries)
    records: list[DeckTemplateRecord] = []

    for query in queries:
        query_key = query.get("queryKey", [])
        data = query.get("state", {}).get("data")
        if not isinstance(data, dict):
            continue

        if source == "meta" and query_key[:1] == ["getGuideDecks"]:
            records.extend(_guide_deck_records(data, refs, source, source_url, fetched_at))
        elif source == "decks" and query_key[:1] == ["meta-decks"]:
            records.extend(_meta_deck_records(data, refs, source, source_url, fetched_at))

    return records


def _guide_deck_records(
    data: dict[str, Any],
    refs: dict[str, dict[str, str]],
    source: str,
    source_url: str,
    fetched_at: str,
) -> list[DeckTemplateRecord]:
    patch_version = _patch_from_guides(data.get("guides", []))
    if patch_version == "unknown":
        patch_version = _infer_patch_version(data)
    guide_decks = data.get("guideDecks") or data.get("guides") or []
    return [
        _record_from_guide_deck(deck, refs, source, source_url, fetched_at, patch_version)
        for deck in _iter_dicts(guide_decks)
    ]


def _meta_deck_records(
    data: dict[str, Any],
    refs: dict[str, dict[str, str]],
    source: str,
    source_url: str,
    fetched_at: str,
) -> list[DeckTemplateRecord]:
    patch_version = _infer_patch_version(data)
    if patch_version == "unknown":
        patch_version = _patch_from_revisions(data.get("patchRevisions", []))
    meta_decks = data.get("metaDeckList") or []
    return [
        _record_from_meta_deck(deck, refs, source, source_url, fetched_at, patch_version)
        for deck in _iter_dicts(meta_decks)
    ]


def _record_from_guide_deck(
    deck: dict[str, Any],
    refs: dict[str, dict[str, str]],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
) -> DeckTemplateRecord:
    name = _first_string(deck, ["name", "title", "deckName", "guideTitle"]) or "unknown"
    slots = deck.get("data", {}).get("slots", []) if isinstance(deck.get("data"), dict) else []
    core_units = [
        _resolve_ref(refs["champions"], slot.get("champion"))
        for slot in slots
        if isinstance(slot, dict) and slot.get("champion")
    ]
    key_items = [
        _resolve_ref(refs["items"], item)
        for slot in slots
        if isinstance(slot, dict)
        for item in slot.get("items", [])
    ]
    traits = [
        _resolve_ref(refs["traits"], trait)
        for trait in deck.get("data", {}).get("traits", [])
    ] if isinstance(deck.get("data"), dict) else []
    return _make_record(
        deck=deck,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        patch_version=patch_version,
        name=name,
        core_units=_dedupe_strings(core_units),
        key_items=_dedupe_strings(key_items),
        traits=_dedupe_strings(traits),
    )


def _record_from_meta_deck(
    deck: dict[str, Any],
    refs: dict[str, dict[str, str]],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
) -> DeckTemplateRecord:
    deck_body = deck.get("deck", {}) if isinstance(deck.get("deck"), dict) else {}
    champions = deck_body.get("champions", [])
    name = _deck_name_from_champions(champions, refs) or _first_string(deck, ["name", "title"]) or "unknown"
    core_units = [
        _resolve_ref(refs["champions"], champion.get("key"))
        for champion in champions
        if isinstance(champion, dict) and champion.get("key")
    ]
    key_items = [
        _resolve_ref(refs["items"], item)
        for champion in champions
        if isinstance(champion, dict)
        for item in champion.get("items", [])
    ]
    traits = [
        _resolve_ref(refs["traits"], trait.get("key"))
        for trait in deck_body.get("traits", [])
        if isinstance(trait, dict) and trait.get("key")
    ]
    return _make_record(
        deck=deck,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        patch_version=patch_version,
        name=name,
        core_units=_dedupe_strings(core_units),
        key_items=_dedupe_strings(key_items),
        traits=_dedupe_strings(traits),
    )


def _make_record(
    *,
    deck: dict[str, Any],
    source: str,
    source_url: str,
    fetched_at: str,
    patch_version: str,
    name: str,
    core_units: list[str],
    key_items: list[str],
    traits: list[str],
) -> DeckTemplateRecord:
    average_place = _first_float(deck, ["avgPlacement", "averagePlace", "avgPlace", "placement"])
    win_rate = _first_float(deck, ["winRate", "win_rate"])
    top4_rate = _first_float(deck, ["top4Rate", "topRate", "top4_rate"])
    play_rate = _first_float(deck, ["pickRate", "playRate", "usageRate"])
    games = _first_int(deck, ["games", "count", "playCount", "totalGames"])
    text = _build_text(name, core_units, key_items, traits, average_place, win_rate, top4_rate, games)
    record_id = _record_id(source, patch_version, name, text)
    return DeckTemplateRecord(
        id=record_id,
        index="deck_templates",
        patch_version=patch_version,
        source=source,
        source_url=source_url,
        fetched_at=fetched_at,
        name=name,
        core_units=core_units,
        key_items=key_items,
        traits=traits,
        average_place=average_place,
        win_rate=win_rate,
        top4_rate=top4_rate,
        play_rate=play_rate,
        games=games,
        text=text,
        metadata={"raw_source": source, "deck_key": str(deck.get("key") or deck.get("deckKey") or "")},
    )


def _queries(next_data: dict[str, Any]) -> list[dict[str, Any]]:
    page_props = next_data.get("props", {}).get("pageProps", {})
    return page_props.get("dehydratedState", {}).get("queries", [])


def _collect_refs(queries: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    refs = {"champions": {}, "items": {}, "traits": {}}
    for query in queries:
        data = query.get("state", {}).get("data")
        if not isinstance(data, dict):
            continue
        if isinstance(data.get("refs"), dict):
            _merge_refs(refs, data["refs"])
        for key, target in (
            ("champions", "champions"),
            ("items", "items"),
            ("traits", "traits"),
        ):
            if isinstance(data.get(key), list):
                _merge_ref_list(refs[target], data[key])
    return refs


def _merge_refs(refs: dict[str, dict[str, str]], raw_refs: dict[str, Any]) -> None:
    for key in ("champions", "items", "traits"):
        if isinstance(raw_refs.get(key), list):
            _merge_ref_list(refs[key], raw_refs[key])


def _merge_ref_list(target: dict[str, str], values: list[Any]) -> None:
    for value in values:
        if not isinstance(value, dict):
            continue
        name = value.get("name")
        if not isinstance(name, str):
            continue
        for key in ("key", "ingameKey", "apiName", "characterName"):
            ref_key = value.get(key)
            if isinstance(ref_key, str):
                target[ref_key] = name
                target[ref_key.replace("TFT17_", "")] = name


def _resolve_ref(refs: dict[str, str], key: Any) -> str:
    if not isinstance(key, str):
        return ""
    return refs.get(key) or refs.get(key.replace("TFT17_", "")) or key


def _deck_name_from_champions(champions: Any, refs: dict[str, dict[str, str]]) -> str | None:
    if not isinstance(champions, list):
        return None
    core = [
        champion
        for champion in champions
        if isinstance(champion, dict) and isinstance(champion.get("coreRank"), int)
    ]
    core.sort(key=lambda champion: champion["coreRank"])
    if not core:
        return None
    return " ".join(_resolve_ref(refs["champions"], champion.get("key")) for champion in core[:2])


def _iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if any(key in value for key in ("name", "deck", "data")):
            yield value
            return
        for child in value.values():
            yield from _iter_dicts(child)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                yield item


def _extract_names(deck: dict[str, Any], keys: list[str]) -> list[str]:
    names: list[str] = []
    for key in keys:
        if key in deck:
            names.extend(_names_from_value(deck[key]))
    return _dedupe_strings(names)


def _names_from_value(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        for key in ("name", "displayName", "characterName", "apiName", "key"):
            if isinstance(value.get(key), str):
                return [value[key]]
        names: list[str] = []
        for child in value.values():
            names.extend(_names_from_value(child))
        return names
    if isinstance(value, list):
        names: list[str] = []
        for item in value:
            names.extend(_names_from_value(item))
        return names
    return []


def _first_string(deck: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = deck.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _first_float(deck: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = deck.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _first_int(deck: dict[str, Any], keys: list[str]) -> int | None:
    for key in keys:
        value = deck.get(key)
        if isinstance(value, int):
            return value
    return None


def _unit_cost(champion: dict[str, Any]) -> int:
    cost = champion.get("cost")
    if isinstance(cost, list) and cost and isinstance(cost[0], int):
        return cost[0]
    if isinstance(cost, int):
        return cost
    return 0


def _trait_champion_lookup(raw_dir: Path) -> dict[str, list[str]]:
    raw_path = raw_dir / "lolchess_champions.json"
    if not raw_path.exists():
        return {}
    document = json.loads(raw_path.read_text(encoding="utf-8"))
    champions = _dedupe_champions(_find_champion_records(document["next_data"]))
    lookup: dict[str, list[str]] = {}
    for champion in champions:
        if not _is_public_champion(champion):
            continue
        name = _first_string(champion, ["name"])
        if not name:
            continue
        for trait in champion.get("traits", []):
            if isinstance(trait, str) and trait:
                lookup.setdefault(trait, []).append(name)
                lookup.setdefault(f"TFT17_{trait}", []).append(name)
    return {key: _dedupe_strings(values) for key, values in lookup.items()}


def _trait_tiers(trait: dict[str, Any]) -> list[int]:
    tiers: list[int] = []
    styles = trait.get("styles")
    if isinstance(styles, list):
        for style in styles:
            if isinstance(style, dict) and isinstance(style.get("min"), int):
                tiers.append(style["min"])
    stats = trait.get("stats")
    if isinstance(stats, dict):
        for key in stats:
            if str(key).isdigit():
                tiers.append(int(key))
    return sorted(set(tiers))


def _trait_summary(trait: dict[str, Any]) -> str:
    desc = _clean_text(_first_string(trait, ["desc", "description", "effect"]) or "")
    stats = trait.get("stats")
    if isinstance(stats, dict) and stats:
        stat_text = ", ".join(f"{key}: {_clean_text(str(value))}" for key, value in sorted(stats.items()))
        return f"{desc} 활성 단계 효과: {stat_text}".strip()
    return desc


def _build_trait_text(*, name: str, tiers: list[int], summary: str, champions: list[str]) -> str:
    parts = [f"{name} is a TFT Set 17 trait."]
    if tiers:
        parts.append(f"Activation tiers: {', '.join(str(tier) for tier in tiers)}.")
    if champions:
        parts.append(f"Units: {', '.join(champions[:20])}.")
    if summary:
        parts.append(summary)
    return " ".join(parts)


def _augment_tier_name(value: Any) -> str:
    try:
        tier = int(value)
    except (TypeError, ValueError):
        tier = 0
    if tier == 1:
        return "silver"
    if tier == 2:
        return "gold"
    if tier == 3:
        return "prismatic"
    return str(value or "unknown")


def _build_augment_text(*, name: str, tier: str, effect: str) -> str:
    parts = [f"{name} is a {tier} TFT Set 17 augment."]
    if effect:
        parts.append(effect)
    return " ".join(parts)


def _clean_playbook_text(page_text: str, title: str) -> str:
    text = page_text
    start = text.rfind(title)
    if start == -1:
        marker = title.split()[0]
        start = text.rfind(marker)
    if start > 0:
        text = text[start:]
    footer = text.find("© LoLCHESS.GG")
    if footer != -1:
        text = text[:footer]
    text = re.sub(r"\s+", " ", text).strip()
    return text[:4000]


def _playbook_title(topic: str) -> str:
    return {
        "role": "역할군",
        "reroll": "리롤 확률",
        "rounds": "라운드 정보",
        "exp": "경험치/골드",
        "damage": "피해량 공식",
        "hotkeys": "단축키",
    }.get(topic, topic)


def _playbook_phase(topic: str) -> str:
    return {
        "role": "all",
        "reroll": "mid",
        "rounds": "all",
        "exp": "all",
        "damage": "all",
        "hotkeys": "all",
    }.get(topic, "all")


def _item_recipe(item: dict[str, Any]) -> str:
    components = item.get("components") or item.get("from")
    if isinstance(components, list):
        names = [
            _first_string(component, ["name", "key"]) if isinstance(component, dict) else str(component)
            for component in components
        ]
        names = [name for name in names if name]
        if names:
            return " + ".join(names)
    from_desc = _clean_text(_first_string(item, ["fromDesc"]) or "")
    return from_desc


def _item_tags(item: dict[str, Any], effect: str) -> list[str]:
    raw = " ".join(
        str(value)
        for value in (
            item.get("key"),
            item.get("name"),
            item.get("desc"),
            item.get("fromDesc"),
            effect,
        )
        if value
    ).lower()
    tags: list[str] = []
    if any(token in raw for token in ("scalead", "attack damage", "ad", "crit", "치명", "공격")):
        tags.append("AD")
    if any(token in raw for token in ("scaleap", "ability power", "ap", "주문", "마법")):
        tags.append("AP")
    if any(token in raw for token in ("health", "armor", "mr", "tank", "체력", "방어", "저항")):
        tags.append("Tank")
    if any(token in raw for token in ("mana", "regen", "마나")):
        tags.append("Mana")
    if any(token in raw for token in ("support", "shield", "heal", "보호막", "회복")):
        tags.append("Support")
    if not tags:
        tags.append("Util")
    return _dedupe_strings(tags)


def _build_item_text(*, name: str, recipe: str, effect: str, tags: list[str]) -> str:
    parts = [f"{name} is a TFT Set 17 item."]
    if recipe:
        parts.append(f"Recipe or stats: {recipe}.")
    if tags:
        parts.append(f"Tags: {', '.join(tags)}.")
    if effect:
        parts.append(effect)
    return " ".join(parts)


def _normalise_role(raw_role: str | None, champion: dict[str, Any]) -> str:
    role = (raw_role or "").lower()
    if "tank" in role:
        return "Tank"
    if "caster" in role or "ap" in role:
        return "Caster"
    if "fighter" in role or "ad" in role:
        return "DPS"
    attack_range = _first_int(champion, ["attackRange"]) or 0
    armor = _first_int(champion, ["armor"]) or 0
    magical_resistance = _first_int(champion, ["magicalResistance"]) or 0
    if armor >= 45 and magical_resistance >= 45 and attack_range <= 2:
        return "Tank"
    if attack_range >= 4:
        return "Caster"
    return "Utility"


def _clean_text(value: str) -> str:
    value = re.sub(r"<br\s*/?>", " ", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"%i:[^) \]]+%?", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _build_unit_text(
    *,
    name: str,
    cost: int,
    traits: list[str],
    role: str,
    skill_name: str | None,
    skill_desc: str | None,
) -> str:
    parts = [f"{name} is a {cost}-cost TFT Set 17 unit."]
    if traits:
        parts.append(f"Traits: {', '.join(traits)}.")
    parts.append(f"Role: {role}.")
    if skill_name:
        parts.append(f"Skill: {skill_name}.")
    if skill_desc:
        parts.append(skill_desc)
    return " ".join(parts)


def _build_text(
    name: str,
    core_units: list[str],
    key_items: list[str],
    traits: list[str],
    average_place: float | None,
    win_rate: float | None,
    top4_rate: float | None,
    games: int | None,
) -> str:
    parts = [f"덱: {name}"]
    if traits:
        parts.append(f"시너지: {', '.join(traits[:8])}")
    if core_units:
        parts.append(f"핵심 유닛: {', '.join(core_units[:12])}")
    if key_items:
        parts.append(f"핵심 아이템: {', '.join(key_items[:12])}")
    stats = []
    if average_place is not None:
        stats.append(f"평균 등수 {average_place}")
    if win_rate is not None:
        stats.append(f"승률 {win_rate}")
    if top4_rate is not None:
        stats.append(f"TOP4 {top4_rate}")
    if games is not None:
        stats.append(f"게임 수 {games}")
    if stats:
        parts.append("통계: " + ", ".join(stats))
    return " | ".join(parts)


def _infer_patch_version(data: dict[str, Any]) -> str:
    text = json.dumps(data, ensure_ascii=False)
    matches = re.findall(r"\bv?(\d{2}\.\d+[a-z]?)\b", text, flags=re.IGNORECASE)
    return matches[0].lower() if matches else "unknown"


def _patch_from_guides(guides: Any) -> str:
    if not isinstance(guides, list):
        return "unknown"
    for guide in guides:
        if not isinstance(guide, dict):
            continue
        name = guide.get("name")
        if not isinstance(name, str):
            continue
        match = re.search(r"\bv?(\d{2}\.\d+[a-z]?)\b", name, flags=re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return "unknown"


def _patch_from_revisions(revisions: Any) -> str:
    if isinstance(revisions, list) and revisions:
        value = revisions[0].get("patchVersion") if isinstance(revisions[0], dict) else None
        if isinstance(value, str):
            return value.lower()
    return "unknown"


def _record_id(source: str, patch_version: str, name: str, text: str) -> str:
    digest = hashlib.sha256(f"{source}|{patch_version}|{name}|{text}".encode()).hexdigest()
    return f"deck_template_{digest[:16]}"


def _unit_record_id(patch_version: str, ingame_key: str) -> str:
    digest = hashlib.sha256(f"units|{patch_version}|{ingame_key}".encode()).hexdigest()
    return f"unit_{digest[:16]}"


def _item_record_id(patch_version: str, key: str) -> str:
    digest = hashlib.sha256(f"items|{patch_version}|{key}".encode()).hexdigest()
    return f"item_{digest[:16]}"


def _trait_record_id(patch_version: str, ingame_key: str) -> str:
    digest = hashlib.sha256(f"traits|{patch_version}|{ingame_key}".encode()).hexdigest()
    return f"trait_{digest[:16]}"


def _augment_record_id(patch_version: str, ingame_key: str) -> str:
    digest = hashlib.sha256(f"augments|{patch_version}|{ingame_key}".encode()).hexdigest()
    return f"augment_{digest[:16]}"


def _playbook_record_id(topic: str) -> str:
    digest = hashlib.sha256(f"playbook|all|{topic}".encode()).hexdigest()
    return f"playbook_{digest[:16]}"


def _dedupe_records(records: list[DeckTemplateRecord]) -> list[DeckTemplateRecord]:
    seen: set[str] = set()
    deduped: list[DeckTemplateRecord] = []
    for record in records:
        key = f"{record.source}|{record.name}|{record.text}"
        if key in seen or record.name == "unknown":
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def _select_patch_version(records: list[DeckTemplateRecord]) -> str:
    versions = [record.patch_version for record in records if record.patch_version != "unknown"]
    if not versions:
        return "unknown"
    return max(versions, key=_patch_sort_key)


def _patch_sort_key(version: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)([a-z]?)$", version, flags=re.IGNORECASE)
    if not match:
        return (0, 0, 0)
    suffix = match.group(3).lower()
    suffix_rank = 0 if not suffix else ord(suffix) - ord("a") + 1
    return (int(match.group(1)), int(match.group(2)), suffix_rank)


def _write_manifest(output_dir: Path, patch_version: str, records: list[DeckTemplateRecord]) -> None:
    manifest = {
        "current_patch": patch_version,
        "index": "deck_templates",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": f"{patch_version}.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_units_manifest(output_dir: Path, patch_version: str, records: list[UnitRecord]) -> None:
    manifest = {
        "current_patch": patch_version,
        "index": "units",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": f"{patch_version}.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_traits_manifest(output_dir: Path, patch_version: str, records: list[TraitRecord]) -> None:
    manifest = {
        "current_patch": patch_version,
        "index": "traits",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": f"{patch_version}.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_items_manifest(output_dir: Path, patch_version: str, records: list[ItemRecord]) -> None:
    manifest = {
        "current_patch": patch_version,
        "index": "items",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": f"{patch_version}.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_augments_manifest(output_dir: Path, patch_version: str, records: list[AugmentRecord]) -> None:
    manifest = {
        "current_patch": patch_version,
        "index": "augments",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": f"{patch_version}.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_playbook_manifest(output_dir: Path, records: list[PlaybookRecord]) -> None:
    manifest = {
        "current_patch": "all",
        "index": "playbook",
        "record_count": len(records),
        "sources": sorted({record.source for record in records}),
        "jsonl_path": "all.jsonl",
    }
    (output_dir / "current_patch.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
