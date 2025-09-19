#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.lib_normalize import load_inputs_and_normalize
from scripts.lib_validate import validate_dataset
from scripts.lib_render import render_markdown, render_index_html


DATA_DIR = ROOT / "data"
DIST_DIR = ROOT / "dist"
INTERNAL_DIR = ROOT / "internal"


def read_categories(path: Path) -> list[str]:
    if not path.exists():
        return []
    cats = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s:
            cats.append(s)
    return cats


def write_json(path: Path, obj: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    include_review = False
    internal_mode = False
    for a in argv:
        if a == "--include-review":
            include_review = True
        if a == "--internal":
            internal_mode = True

    out_dir = INTERNAL_DIR if internal_mode else DIST_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    categories = read_categories(DATA_DIR / "categories.txt")

    dataset = load_inputs_and_normalize(
        karaoke_path=DATA_DIR / "karaoke_song_list.json",
        to_review_path=DATA_DIR / "to_review.json",
        categories=categories,
        include_review=include_review and internal_mode,
    )

    # Attach simple meta
    dataset.setdefault("meta", {})
    dataset["meta"].update(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": 1,
        }
    )

    # Validate
    report = validate_dataset(dataset, categories)
    write_json(out_dir / "validation_report.json", report)

    # Emit songbook.json
    write_json(out_dir / "songbook.json", dataset)

    # Emit songbook.md
    md = render_markdown(dataset, categories)
    (out_dir / "songbook.md").write_text(md, encoding="utf-8")

    # Emit index.html (client-driven)
    html = render_index_html(dataset)
    (out_dir / "index.html").write_text(html, encoding="utf-8")

    target_label = "internal" if internal_mode else "dist"
    print("Built:")
    print(f" - {target_label}/songbook.json")
    print(f" - {target_label}/songbook.md")
    print(f" - {target_label}/validation_report.json")
    print(f" - {target_label}/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
