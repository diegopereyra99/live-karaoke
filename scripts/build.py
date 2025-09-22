#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.lib_normalize import load_inputs_and_normalize
from scripts.lib_validate import validate_dataset
from scripts.lib_render import render_markdown
from scripts.lib_search_index import build_search_index


DATA_DIR = ROOT / "data"
DIST_DIR = ROOT / "dist"
INTERNAL_DIR = ROOT / "internal"
WEB_DIR = ROOT / "web"


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


def copy_static_frontend(out_dir: Path) -> None:
    if not WEB_DIR.exists():
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    # Copy top-level files
    for name in ("index.html", "styles.css", "app.js"):
        src = WEB_DIR / name
        if src.exists():
            shutil.copy2(src, out_dir / name)
    # Copy optional shared theme from repo root if present
    theme_src = ROOT / "theme.css"
    if theme_src.exists():
        shutil.copy2(theme_src, out_dir / "theme.css")
    # Copy assets directory recursively
    assets_src = WEB_DIR / "assets"
    assets_dst = out_dir / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)


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

    # Emit search_index.json
    search_index = build_search_index(dataset)
    write_json(out_dir / "search_index.json", search_index)

    # Emit songbook.md
    md = render_markdown(dataset, categories)
    (out_dir / "songbook.md").write_text(md, encoding="utf-8")

    # Copy static frontend (index.html, styles.css, app.js, assets)
    copy_static_frontend(out_dir)

    target_label = "internal" if internal_mode else "dist"
    print("Built:")
    print(f" - {target_label}/songbook.json")
    print(f" - {target_label}/search_index.json")
    print(f" - {target_label}/songbook.md")
    print(f" - {target_label}/validation_report.json")
    if (out_dir / "index.html").exists():
        print(f" - {target_label}/index.html")
    if (out_dir / "styles.css").exists():
        print(f" - {target_label}/styles.css")
    if (out_dir / "app.js").exists():
        print(f" - {target_label}/app.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
