"""유튜브 자막 fetch 도구.

질문이나 검색 결과가 유튜브 영상을 가리킬 때 영상 내용을 근거로 쓰기 위해
자막을 가져온다. 별도 패키지 없이 YouTube timedtext endpoint를 사용한다.

주의:
- whitelist.yaml에 allowed_youtube_channels가 비어 있으면 모든 채널을 허용한다.
- 값이 들어 있으면 watch page에서 channelId를 읽어 허용 채널인지 검사한다.
- 한국어 자막을 우선 시도하고, 없으면 영어 자막을 시도한다.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

from app.research.state import Transcript
from app.research.whitelist import is_allowed_youtube_channel

from .base import USER_AGENT, ResearchToolError


VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
CHANNEL_RE = re.compile(r'"channelId"\s*:\s*"([^"]+)"')
TITLE_RE = re.compile(r'"title"\s*:\s*\{"runs"\s*:\s*\[\{"text"\s*:\s*"([^"]+)"')


def extract_video_id(value: str) -> str | None:
    """영상 ID 또는 YouTube URL에서 11자 video_id를 추출한다."""
    value = value.strip()
    if VIDEO_ID_RE.match(value):
        return value
    parsed = urlparse(value)
    if parsed.netloc.endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        return candidate if VIDEO_ID_RE.match(candidate) else None
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        candidate = qs.get("v", [None])[0]
        if candidate and VIDEO_ID_RE.match(candidate):
            return candidate
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"shorts", "embed"}:
            return parts[1] if VIDEO_ID_RE.match(parts[1]) else None
    return None


async def _fetch_watch_metadata(client: httpx.AsyncClient, video_id: str) -> tuple[str | None, str | None]:
    """watch page에서 channelId와 title을 읽는다.

    channelId는 whitelist 검사용이고 title은 Source 제목으로 쓰기 위한 보조 정보다.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = await client.get(url)
    response.raise_for_status()
    html = response.text
    channel = CHANNEL_RE.search(html)
    title = TITLE_RE.search(html)
    return (
        channel.group(1) if channel else None,
        json.loads(f'"{title.group(1)}"') if title else None,
    )


def _extract_json3_text(payload: dict) -> str:
    """timedtext json3 응답에서 자막 조각을 하나의 문자열로 합친다."""
    parts: list[str] = []
    for event in payload.get("events", []):
        for segment in event.get("segs", []) or []:
            text = segment.get("utf8")
            if text:
                parts.append(text)
    return " ".join(" ".join(parts).split())


def _extract_xml_text(payload: str) -> str:
    """일부 응답이 XML로 올 때를 위한 fallback parser."""
    root = ET.fromstring(payload)
    return " ".join(" ".join(node.text or "" for node in root.findall(".//text")).split())


async def youtube_transcript(video_id: str) -> Transcript:
    """한국어 자막을 먼저 가져오고, 없으면 영어 자막을 fallback으로 시도한다."""
    resolved = extract_video_id(video_id)
    if not resolved:
        raise ResearchToolError(f"invalid_youtube_video_id: {video_id}")

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=6.0,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        channel_id, title = await _fetch_watch_metadata(client, resolved)
        if not is_allowed_youtube_channel(channel_id):
            raise ResearchToolError(f"youtube_channel_not_whitelisted: {channel_id}")

        for language in ("ko", "en"):
            # fmt=json3이 기본이지만, 실제 응답이 XML로 올 수 있어 아래에서 둘 다 처리한다.
            query = urlencode({"v": resolved, "lang": language, "fmt": "json3"})
            response = await client.get(f"https://video.google.com/timedtext?{query}")
            if response.status_code >= 400 or not response.text.strip():
                continue
            try:
                text = _extract_json3_text(response.json())
            except ValueError:
                text = _extract_xml_text(response.text)
            if text:
                return Transcript(
                    video_id=resolved,
                    text=text[:12000],
                    language=language,
                    title=title,
                    source_url=f"https://www.youtube.com/watch?v={resolved}",
                )

    raise ResearchToolError(f"youtube_transcript_unavailable: {resolved}")
