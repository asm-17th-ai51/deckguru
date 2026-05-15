import re

from app.observability import render_console_event


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def test_render_console_event_formats_request_start():
    line = render_console_event(
        {
            "timestamp": "12:13:44",
            "level": "info",
            "event": "request_start",
            "stage": "api",
            "method": "POST",
            "path": "/api/recommend",
            "request_id": "c76ab51b-121b-4420-bb5f-dafce965027c",
        }
    )

    assert line == "12:13:44 INFO  [api] -> POST /api/recommend req=c76ab51b"


def test_render_console_event_formats_request_done_without_duplicate_details():
    line = render_console_event(
        {
            "timestamp": "12:14:12",
            "level": "info",
            "event": "request_done",
            "stage": "api",
            "method": "POST",
            "path": "/api/recommend",
            "request_id": "c76ab51b-121b-4420-bb5f-dafce965027c",
            "status_code": 200,
            "latency_ms": 27719,
            "cache": "MISS",
        }
    )

    assert line == "12:14:12 INFO  [api] <- 200 MISS 27719ms req=c76ab51b"


def test_render_console_event_keeps_stage_first_and_compacts_details():
    line = render_console_event(
        {
            "timestamp": "12:13:58",
            "level": "info",
            "event": "rag_done",
            "stage": "rag",
            "request_id": "c76ab51b-121b-4420-bb5f-dafce965027c",
            "method": "POST",
            "path": "/api/recommend",
            "chunks": 5,
            "avg_score": 0.13,
            "warning": "rag_avg_score_low",
            "latency_ms": 11040,
        }
    )

    assert line == (
        "12:13:58 INFO  [rag] done chunks=5 avg=0.13 "
        "warning=rag_avg_score_low 11040ms req=c76ab51b"
    )


def test_render_console_event_compacts_lists_and_dicts():
    line = render_console_event(
        {
            "timestamp": "12:14:12",
            "level": "info",
            "event": "rag_whitelist_load_done",
            "stage": "rag",
            "counts": {"units": 63, "items": 188, "traits": 69, "augments": 259},
            "collections": ["deck_templates", "augments", "traits"],
        }
    )

    assert line == (
        "12:14:12 INFO  [rag] whitelist load done "
        "collections=deck_templates,augments,traits "
        "counts=units:63,items:188,traits:69,augments:259"
    )


def test_render_console_event_can_colorize_console_output():
    event = {
        "timestamp": "12:13:58",
        "level": "warning",
        "event": "rag_search_unavailable",
        "stage": "rag",
        "request_id": "c76ab51b-121b-4420-bb5f-dafce965027c",
        "index": "traits",
        "error": "RAG collection traits is not available",
    }

    plain = render_console_event(event)
    colored = render_console_event(event, colors=True)

    assert "\x1b[" in colored
    assert ANSI_RE.sub("", colored) == plain
