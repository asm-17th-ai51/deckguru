from enum import Enum


class Tier(str, Enum):
    IRON = "IRON"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    EMERALD = "EMERALD"
    DIAMOND = "DIAMOND"
    MASTER_PLUS = "MASTER+"


class PlayStyle(str, Enum):
    stable_top4 = "stable_top4"
    high_risk_first = "high_risk_first"
    easy_beginner = "easy_beginner"
    flexible = "flexible"


class Intent(str, Enum):
    recommend_deck = "recommend_deck"
    deck_playstyle = "deck_playstyle"
    item_pivot = "item_pivot"
    patch_summary = "patch_summary"
    other = "other"


class Confidence(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Phase(str, Enum):
    early = "early"
    mid = "mid"
    late = "late"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class SourceKind(str, Enum):
    patch_note_official = "patch_note_official"
    meta_site = "meta_site"
    community_post = "community_post"
    youtube = "youtube"
