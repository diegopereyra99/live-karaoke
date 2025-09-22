from __future__ import annotations

from typing import Any, Iterable


def _norm(s: str) -> str:
    try:
        import unicodedata
        s = unicodedata.normalize("NFKD", s or "")
        s = "".join(ch for ch in s if not unicodedata.combining(ch))
    except Exception:
        s = s or ""
    return s.lower().strip()


def _trigrams(s: str) -> list[str]:
    s = f"  {s}  "  # pad to allow edge trigrams
    out: list[str] = []
    for i in range(len(s) - 2):
        out.append(s[i : i + 3])
    # dedupe while preserving order
    seen = set()
    uniq: list[str] = []
    for g in out:
        if g not in seen:
            uniq.append(g)
            seen.add(g)
    return uniq


def build_search_index(dataset: dict[str, Any]) -> dict[str, Any]:
    # Produce a compact index for client fuzzy search
    entries: list[dict[str, Any]] = []
    for s in dataset.get("songs", []):
        title = (s.get("title") or "").strip()
        artist = (s.get("artist") or "").strip()
        categories = []
        if isinstance(s.get("categories"), list):
            categories = [c.strip() for c in s.get("categories") if isinstance(c, str) and c.strip()]
        else:
            c = (s.get("category") or "Uncategorized").strip()
            if c:
                categories = [c]
        nid = s.get("id") or ""

        nt = _norm(title)
        na = _norm(artist)
        nc = _norm(" ".join(categories))
        hay = f"{nt} {na} {nc}"
        grams = _trigrams(hay)

        entries.append({
            "id": nid,
            "t": nt,  # normalized title
            "a": na,  # normalized artist
            "c": nc,  # normalized categories (joined)
            "g": grams,  # trigrams
        })

    return {"version": 1, "songs": entries}
