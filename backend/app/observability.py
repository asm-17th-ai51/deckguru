"""Small logging helpers for request-flow observability."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

_SKIP_DETAIL_KEYS = {
    "event",
    "level",
    "timestamp",
    "stage",
    "request_id",
    "method",
    "path",
}

_DETAIL_ALIASES = {
    "avg_score": "avg",
    "rag_avg_score": "rag_avg",
    "status_code": "status",
}

_DETAIL_ORDER = (
    "intent",
    "role",
    "model",
    "index",
    "collections",
    "query",
    "chunks",
    "hits",
    "top_score",
    "avg_score",
    "rag_avg_score",
    "decks",
    "candidates",
    "sources",
    "warnings",
    "warning",
    "counts",
    "latency_ms",
)

_ANSI_RESET = "\x1b[0m"
_ANSI_DIM = "2"
_ANSI_BOLD = "1"

_LEVEL_COLORS = {
    "DEBUG": "36",
    "INFO": "32",
    "WARNING": "33",
    "ERROR": "31",
    "CRITICAL": "1;31",
}

_STAGE_COLORS = {
    "api": "36",
    "intent": "35",
    "rag": "32",
    "research": "34",
    "llm": "33",
    "meta": "95",
    "recommend": "96",
    "grounding": "93",
    "response": "92",
    "strategy": "97",
    "patch_info": "94",
}


def elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def preview(value: Any, *, limit: int = 80) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def console_log_renderer(colors: bool = False) -> Callable[[Any, str, dict[str, Any]], str]:
    def _renderer(logger: Any, method_name: str, event_dict: dict[str, Any]) -> str:
        del logger, method_name
        return render_console_event(event_dict, colors=colors)

    return _renderer


def render_console_event(event_dict: dict[str, Any], *, colors: bool = False) -> str:
    event = str(event_dict.get("event", "-"))
    stage = str(event_dict.get("stage") or _stage_from_event(event))
    timestamp = str(event_dict.get("timestamp", "-"))
    level_name = str(event_dict.get("level", "info")).upper()
    level = level_name.ljust(5)
    request_id = _short_request_id(event_dict.get("request_id"))

    message = _event_message(event, event_dict)
    details = _format_details(event_dict)
    timestamp_part = _color(timestamp, _ANSI_DIM, colors)
    level_part = _color(level, _LEVEL_COLORS.get(level_name, "37"), colors)
    stage_part = _color(f"[{stage}]", _STAGE_COLORS.get(stage, _ANSI_BOLD), colors)
    parts = [f"{timestamp_part} {level_part} {stage_part}", _color(message, _ANSI_BOLD, colors)]
    if details:
        parts.append(_color(details, _ANSI_DIM, colors))
    if request_id:
        parts.append(_color(f"req={request_id}", _ANSI_DIM, colors))
    return " ".join(part for part in parts if part)


def _stage_from_event(event: str) -> str:
    if event.startswith("request_") or event.startswith("cache_"):
        return "api"
    return event.split("_", 1)[0] if "_" in event else "app"


def _event_message(event: str, event_dict: dict[str, Any]) -> str:
    if event == "request_start":
        method = event_dict.get("method", "-")
        path = event_dict.get("path", "-")
        return f"-> {method} {path}"
    if event == "request_done":
        status = event_dict.get("status_code", "-")
        cache = event_dict.get("cache")
        latency = _format_latency(event_dict.get("latency_ms"))
        return " ".join(part for part in ("<-", str(status), str(cache or ""), latency) if part)
    if event == "request_error":
        latency = _format_latency(event_dict.get("latency_ms"))
        return f"!! error {latency}".rstrip()

    stage = str(event_dict.get("stage") or _stage_from_event(event))
    label = event
    if label.startswith(f"{stage}_"):
        label = label[len(stage) + 1 :]
    return label.replace("_", " ")


def _format_details(event_dict: dict[str, Any]) -> str:
    skip_keys = set(_SKIP_DETAIL_KEYS)
    if str(event_dict.get("event", "")).startswith("request_"):
        skip_keys.update({"cache", "latency_ms", "status_code"})

    keys = [key for key in _DETAIL_ORDER if key in event_dict and key not in skip_keys]
    keys.extend(
        sorted(
            key
            for key in event_dict
            if key not in skip_keys
            and key not in keys
            and key != "latency_ms"
        )
    )

    fields: list[str] = []
    for key in keys:
        value = event_dict.get(key)
        if value is None:
            continue
        if key == "latency_ms":
            fields.append(_format_latency(value))
            continue
        fields.append(f"{_DETAIL_ALIASES.get(key, key)}={_format_value(value)}")
    return " ".join(field for field in fields if field)


def _format_value(value: Any) -> str:
    if isinstance(value, dict):
        return ",".join(f"{key}:{_format_value(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return ",".join(_format_value(item) for item in value)
    return preview(value, limit=96)


def _format_latency(value: Any) -> str:
    if value is None:
        return ""
    return f"{value}ms"


def _short_request_id(value: Any) -> str:
    if not value or value == "-":
        return ""
    return str(value)[:8]


def _color(text: str, code: str, enabled: bool) -> str:
    if not enabled or not text:
        return text
    return f"\x1b[{code}m{text}{_ANSI_RESET}"
