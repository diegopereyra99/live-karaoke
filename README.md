# Live Karaoke Paris — Songbook Builder

## Overview

- Builds a searchable songbook website from JSON inputs.
- Enriches songs with `lyrics_url` (Musixmatch-style) and a Google `fallback_url` when missing.
- Ships a static site in `dist/` for GitHub Pages.

## Live Site

- URL: https://diegopereyra99.github.io/livekaraoke-songlist/
- QR Code (to GitHub Pages):

  ![QR to Live Site](https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=https%3A%2F%2Fdiegopereyra99.github.io%2Flivekaraoke-songlist%2F)

## Quick Start

- Requirements: Python 3.9+ (standard library only)
- Data files live under `data/`:
  - `karaoke_song_list.json` (main list; may contain `lyrics_url` already)
  - `to_review.json` (optional; excluded from public builds)
  - `categories.txt` (canonical categories and order)

## Build Modes

- Public build (default):
  - Command: `python3 scripts/build.py`
  - Outputs to `dist/`:
    - `songbook.json` (normalized data for client)
    - `search_index.json` (client-side search index)
    - `songbook.md` (readable markdown)
    - `validation_report.json` (issues found, if any)
    - `karaoke_song_list.json` (input list enriched with any missing lyrics/fallback URLs)

- Internal build (for local review only):
  - Command: `python3 scripts/build.py --internal --include-review`
  - Writes to `internal/` (gitignored). Do not publish.
  - Important: The public build always excludes `to_review.json`.

## Data Updates

- Apply a batch of new lyrics links locally (out of band from build):
  - Place your updates in `data/lyrics_updates.json` (or pass a path).
  - Run: `python3 scripts/apply_lyrics_updates.py` \
    or `python3 scripts/apply_lyrics_updates.py --updates ./lyrics_updates.json --data ./data/karaoke_song_list.json`
  - The script updates `data/karaoke_song_list.json` setting `lyrics_url = new_url` for matched songs.

## Validation

- Build first: `python3 scripts/build.py`
- Optional checks (if you have a checker):
  - `python3 scripts/check_lyrics_urls.py --input dist/karaoke_song_list.json --output dist/lyrics_url_report.json`
  - Exit code is non‑zero if failures are found; see the JSON report for details.

## Deploy

- Publish the contents of `dist/` to GitHub Pages (Project Pages):
  - Branch: `gh-pages` (recommended) or via GitHub Actions copying `dist/`.
  - Ensure paths are relative so it serves under `/livekaraoke-songlist/`.

## References

- See `SPEC.md` for data model and repository goals.
