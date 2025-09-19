from __future__ import annotations

from typing import Any


def validate_dataset(dataset: dict[str, Any], categories: list[str]) -> dict:
    issues: list[dict] = []
    cat_set = set(categories) | {"Uncategorized"}

    for s in dataset.get("songs", []):
        sid = s.get("id")
        title = (s.get("title") or "").strip()
        artist = (s.get("artist") or "").strip()
        category = (s.get("category") or "").strip() or "Uncategorized"

        if not title:
            issues.append({"id": sid, "field": "title", "error": "missing"})
        if not artist:
            issues.append({"id": sid, "field": "artist", "error": "missing"})
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

