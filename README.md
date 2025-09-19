Live Karaoke Paris — Songbook Builder (MVP)

Quick start

- Requirements: Python 3.9+ (standard library only)
- Data files live under `data/`:
  - `karaoke_song_list.json` (main list)
  - `to_review.json` (optional)
  - `categories.txt` (canonical categories and order)

Build artifacts

- Public build (excludes review songs): `python3 scripts/build.py`
- Outputs to `dist/`:
  - `songbook.json` (normalized data for client)
  - `songbook.md` (readable markdown)
  - `validation_report.json` (issues found, if any)

Internal-only build (unsafe to publish!)

- Includes `to_review.json` but writes to `internal/` which is gitignored.
- Run: `python3 scripts/build.py --internal --include-review`
- Outputs to `internal/` and must not be published or committed.

Important: Do NOT publish songs from `to_review.json`. The default public build always excludes them; only the internal build includes them and writes to a non‑tracked folder.

Notes

- `index.html` and `search_index.json` will be added next per SPEC.md.
- See `SPEC.md` for details on data model and repository goals.
