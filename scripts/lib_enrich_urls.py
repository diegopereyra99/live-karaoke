from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlencode


def _ascii_strip_accents(s: str) -> str:
    if not isinstance(s, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


_RE_FEATURING = re.compile(r"\s+(feat\.?|ft\.?|featuring)\b.*$", re.IGNORECASE)
_RE_PARENS = re.compile(r"\s*\([^)]*\)")
_RE_SUFFIX = re.compile(r"\s*-\s*(Remastered|Live|Version)\b.*$", re.IGNORECASE)


def _clean_artist_for_slug(artist: str) -> str:
    artist = _ascii_strip_accents(artist or "").strip()
    # Remove featuring tails
    artist = _RE_FEATURING.sub("", artist)
    return artist


def _clean_title_for_slug(title: str) -> str:
    title = _ascii_strip_accents(title or "").strip()
    # Remove content in parentheses
    title = _RE_PARENS.sub("", title).strip()
    # Remove common suffixes
    title = _RE_SUFFIX.sub("", title).strip()
    # Special case YMCA
    letters_only = re.sub(r"[^A-Za-z]+", "", title).upper()
    if letters_only == "YMCA":
        return "Y.M.C.A."
    return title


def _slugify_for_musixmatch(s: str) -> str:
    # Keep case as-is; rules don't require lowercasing
    s = s.replace("&", " and ")
    # Replace underscores and slashes with spaces before hyphenation
    s = re.sub(r"[\s_/]+", " ", s).strip()
    # Replace apostrophes with hyphens (both straight and curly)
    s = s.replace("'", "-").replace("’", "-").replace("‘", "-")
    # Remove punctuation except '.' and '-'
    kept = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat.startswith("P") and ch not in (".", "-"):
            continue
        kept.append(ch)
    s = "".join(kept)
    # Spaces to hyphens, collapse multiple hyphens
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-+", "-", s)
    s = s.strip("-")
    return s


def build_musixmatch_url(artist: str, title: str) -> str:
    artist_clean = _clean_artist_for_slug(artist)
    title_clean = _clean_title_for_slug(title)
    artist_slug = _slugify_for_musixmatch(artist_clean)
    title_slug = _slugify_for_musixmatch(title_clean)
    return f"https://www.musixmatch.com/lyrics/{artist_slug}/{title_slug}"


def _query_keyword_for_category(category: str | None, categories_list: list[str] | None = None) -> str:
    # Accept either a single category string or a list of categories
    c = (category or "").strip()
    cats = [c] if c else []
    if categories_list:
        cats.extend([x for x in categories_list if isinstance(x, str)])

    # Choose keyword based on any matching category
    if any(x in ("Latin", "Portuguese") for x in cats):
        return "letra"
    if any(x in ("Italian", "Italian Classics") for x in cats):
        return "testo"
    return "lyrics"


def build_google_fallback_url(title: str, artist: str, category: str | None, categories_list: list[str] | None = None) -> str:
    keyword = _query_keyword_for_category(category, categories_list)
    # Use quotes around title as requested
    query = f'{keyword} "{title}" {artist}'.strip()
    params = {"q": query, "hl": "en", "gl": "US", "pws": "0"}
    return f"https://www.google.com/search?{urlencode(params)}"


def _pick_first(d: dict, keys: list[str]) -> str | None:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def enrich_karaoke_json(input_path: Path) -> list[dict]:
    """
    Load karaoke_song_list.json (list of dicts) and return a new list with
    missing fields 'lyrics_url' and 'fallback_url' added, without overwriting
    existing values. Idempotent by design.
    """
    if not input_path.exists():
        return []
    items = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        return []

    out: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        rec = dict(item)
        title = _pick_first(rec, ["name", "title", "song"]) or ""
        artist = _pick_first(rec, ["artist", "singer", "band"]) or ""
        raw_cat = rec.get("category")
        category = raw_cat if isinstance(raw_cat, str) else None
        categories_list = raw_cat if isinstance(raw_cat, list) else None

        if not rec.get("lyrics_url") and title and artist:
            rec["lyrics_url"] = build_musixmatch_url(artist, title)

        if not rec.get("fallback_url") and (title or artist):
            rec["fallback_url"] = build_google_fallback_url(title, artist, category, categories_list)

        out.append(rec)
    return out
