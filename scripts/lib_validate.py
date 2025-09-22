from __future__ import annotations

from typing import Any


def validate_dataset(dataset: dict[str, Any], categories: list[str]) -> dict:
    issues: list[dict] = []
    cat_set = set(categories) | {"Uncategorized"}

    for s in dataset.get("songs", []):
        sid = s.get("id")
        title = (s.get("title") or "").strip()
        artist = (s.get("artist") or "").strip()
        categories_val = s.get("categories")
        if isinstance(categories_val, list):
            cats = [str(c).strip() or "Uncategorized" for c in categories_val if str(c).strip() or "Uncategorized"]
        else:
            cats = [((s.get("category") or "").strip() or "Uncategorized")]

        if not title:
            issues.append({"id": sid, "field": "title", "error": "missing"})
        if not artist:
            issues.append({"id": sid, "field": "artist", "error": "missing"})
        for category in cats:
            if category not in cat_set:
                issues.append(
                    {
                        "id": sid,
                        "field": "category",
                        "error": "invalid_category",
                        "value": category,
                    }
                )

    return {
        "summary": {
            "songs": len(dataset.get("songs", [])),
            "artists": len(dataset.get("artists", [])),
            "categories": len(dataset.get("categories", [])),
            "issues": len(issues),
        },
        "issues": issues,
    }
