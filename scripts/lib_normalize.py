from __future__ import annotations

import json
import unicodedata
import re
from pathlib import Path
from typing import Iterable


def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    # Accept either list or object with categories mapping
    if isinstance(data, dict) and "categories" in data and isinstance(data["categories"], dict):
        songs: list[dict] = []
        for cat, items in data["categories"].items():
            for it in items or []:
                if isinstance(it, dict):
                    it = dict(it)
                    it.setdefault("category", cat)
                songs.append(it)
        return songs
    if isinstance(data, list):
        return data
    raise ValueError(f"Unsupported JSON structure in {path}")


def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = s.strip()
    return s


_SLUG_SAFE = re.compile(r"[^a-z0-9-]+")


def slugify(s: str) -> str:
    s = _normalize_text(s)
    s = s.replace("&", " and ")
    s = re.sub(r"[\s_/]+", "-", s)
    s = _SLUG_SAFE.sub("", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def _pick(d: dict, keys: Iterable[str]) -> str | None:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return None


def _map_fields(raw: dict) -> dict:
    out: dict = {}
    title = _pick(raw, ("title", "song", "name", "track"))
    artist = _pick(raw, ("artist", "singer", "band"))
    category = _pick(raw, ("category", "genre", "style", "cat"))
    lyrics = _pick(raw, ("lyrics_url", "lyrics", "letra", "url_letra"))

    if title:
        out["title"] = title.strip()
    if artist:
        out["artist"] = artist.strip()
    if category:
        out["category"] = category.strip()
    if lyrics and re.match(r"^https?://", lyrics.strip(), re.I):
        out["lyrics_url"] = lyrics.strip()

    # keep extra fields for future, but not used in v1
    for k, v in raw.items():
        if k not in out:
            out.setdefault("extra", {})[k] = v
    return out


def _dedupe_songs(songs: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    out: list[dict] = []
    for s in songs:
        t = _normalize_text(s.get("title", ""))
        a = _normalize_text(s.get("artist", ""))
        key = (a, t)
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out




def _build_artists(songs: list[dict]) -> list[dict]:
    by_slug: dict[str, dict] = {}
    for s in songs:
        name = s.get("artist", "").strip()
        if not name:
            continue
        slug = slugify(name)
        if slug not in by_slug:
            by_slug[slug] = {"id": f"artist:{slug}", "name": name, "slug": slug}
    artists = list(by_slug.values())
    artists.sort(key=lambda x: _normalize_text(x["name"]))
    return artists


def load_inputs_and_normalize(
    karaoke_path: Path,
    to_review_path: Path,
    categories: list[str],
    include_review: bool = False,
) -> dict:
    base = _read_json(karaoke_path)
    extra = _read_json(to_review_path) if (include_review and to_review_path.exists()) else []

    songs = []
    for raw in [*_ensure_list(base), *_ensure_list(extra)]:
        mapped = _map_fields(raw if isinstance(raw, dict) else {})
        if not mapped.get("category"):
            mapped["category"] = "Uncategorized"
        # Validate against categories list later; keep as-is for now
        songs.append(mapped)

    songs = _dedupe_songs(songs)

    # Enrich with ids
    for s in songs:
        a_slug = slugify(s.get("artist", "unknown")) or "unknown"
        t_slug = slugify(s.get("title", "untitled")) or "untitled"
        s["id"] = f"song:{a_slug}:{t_slug}"
        s["artist_id"] = f"artist:{a_slug}"

    artists = _build_artists(songs)

    # Categories output: ordered by provided list + ensure 'Uncategorized' last if present
    out_categories = list(categories)
    if "Uncategorized" not in out_categories:
        out_categories.append("Uncategorized")

    dataset = {
        "categories": out_categories,
        "artists": artists,
        "songs": sorted(
            songs,
            key=lambda s: (
                out_categories.index(s.get("category", "Uncategorized"))
                if s.get("category", "Uncategorized") in out_categories
                else len(out_categories),
                _normalize_text(s.get("artist", "")),
                _normalize_text(s.get("title", "")),
            ),
        ),
    }
    return dataset


def _ensure_list(x) -> list:
    if isinstance(x, list):
        return x
    return []
