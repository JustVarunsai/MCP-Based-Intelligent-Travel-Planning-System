from typing import Any
import re

import httpx

from mcp_server._app import mcp
from mcp_server.config import config

WIKIVOYAGE_URL = "https://en.wikivoyage.org/w/api.php"

_LINK_RE = re.compile(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]")
_TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}")
_FORMAT_RE = re.compile(r"'{2,}")
_LISTING_RE = re.compile(r"^\*\s*", flags=re.MULTILINE)


def _clean_wikitext(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = _TEMPLATE_RE.sub("", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _FORMAT_RE.sub("", text)
    text = _LISTING_RE.sub("• ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


@mcp.tool()
def search_destinations(
    query: str,
    sections: list[str] | None = None,
    max_chars: int = 4000,
) -> dict[str, Any]:
    """Wikivoyage destination guide. sections defaults to ['See','Do','Eat','Sleep']. Returns cleaned plain text per section."""
    sections = sections or ["See", "Do", "Eat", "Sleep"]

    try:
        resp = httpx.get(
            WIKIVOYAGE_URL,
            params={
                "action": "parse",
                "page": query,
                "prop": "wikitext",
                "format": "json",
                "redirects": 1,
            },
            headers={"User-Agent": config.USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"error": f"Wikivoyage request failed: {e}"}

    if "error" in data or "parse" not in data:
        return {"error": f"No Wikivoyage page for '{query}'"}

    parse = data["parse"]
    title = parse.get("title", query)
    wikitext = (parse.get("wikitext") or {}).get("*", "")
    if not wikitext:
        return {"error": "Empty page"}

    section_map: dict[str, str] = {}
    current = "Lede"
    buf: list[str] = []
    for line in wikitext.splitlines():
        m = re.match(r"^==\s*([^=]+?)\s*==\s*$", line)
        if m:
            if buf:
                section_map[current] = _clean_wikitext("\n".join(buf))
            current = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        section_map[current] = _clean_wikitext("\n".join(buf))

    wanted = ["Lede"] + sections
    out = {}
    total = 0
    for s in wanted:
        if s not in section_map:
            continue
        text = section_map[s]
        if total + len(text) > max_chars:
            text = text[: max_chars - total] + "…"
        out[s] = text
        total += len(text)
        if total >= max_chars:
            break

    return {
        "destination": title,
        "url": f"https://en.wikivoyage.org/wiki/{title.replace(' ', '_')}",
        "sections": out,
    }
