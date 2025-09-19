# Live Karaoke Paris – Repo Spec v1

> **Goal:** a simple and robust repository to **manage the song list** (JSON datasets + `categories.txt`) and **generate** two public artifacts: (1) a **readable Markdown** for internal use and (2) a **static HTML page** (GitHub Pages) with navigation by category, advanced search, and (later) links to lyrics.

---

## 1) Scope of v1 (MVP)

### 1.1 Features

* **Client‑driven site**: `index.html` loads data from JSON at runtime (no pre‑rendered HTML lists). The Python build stays **minimal** and only prepares data files.
* **Markdown generator** (`songbook.md`)

  * Sorted by **Category → Artist → Title**.
  * Headings per category and artist.
* **Static site** (`index.html`)

  * One `<details>` accordion per **Category** (no nested accordions per artist).
  * **Live search** filtering by text (matches title/artist/category).
  * **Fuzzy artist lookup with suggestions** (bar‑proof): typo‑tolerant, diacritic/case‑insensitive, non‑prefix matches; shows **Artists** and **Songs** buckets; keyboard nav + scroll‑to/highlight.
  * The **All Songs** view is *not* expanded by default. If included and expanded, it should appear at the end.
* **Data normalization** (via Python build)

  * Unifies inputs into a compact, frontend‑friendly schema.
  * Produces `songbook.json` (normalized songs + categories + artists) and `search_index.json` (precomputed, small, for fuzzy search).
* **Validator**

  * Checks required fields and categories; writes `validation_report.json`.

### 1.2 Out of immediate scope (but planned) Out of immediate scope (but planned)

* Web editing panel.
* Lyrics links (see Roadmap).
* API integrations.
* Multi-language UI (v1 only EN, copy easy to extend to ES/FR later).

---

## 2) Input data and model

### 2.1 Input files

* `karaoke_song_list.json`: **official** song list (any supported format, normalized).
* `to_review.json`: **optional** list of songs under review. Included in artifacts only if flagged as ready (e.g. `status: "ready" | "ok" | true`).
* `categories.txt`: **canonical list** and **order** of categories (one per line). Example:

  ```
  Rock
  Pop
  R&B/Funk
  Jazz/Swing
  Disco/Dance
  Latin
  Italian
  Musicals & Standards
  ```

### 2.2 Normalized song model

```ts
Song = {
  title: string,          // required, trimmed
  artist: string,         // required, trimmed
  category: string,       // required; if missing → "Uncategorized"; validated against categories.txt
  lyrics_url?: string,    // optional; for later versions
  // extra fields preserved but not used in v1
}
```

### 2.3 Normalization rules

* Map synonyms:

  * `title` ← `song|name|track`
  * `artist` ← `singer|band`
  * `category` ← `genre|style|cat`
  * `lyrics_url` ← `lyrics|letra|url_letra` (only if URL-like)
* If JSON has `{"categories": {"Pop": [ ... ]}}`, set `category = key` when missing.
* Trim and remove exact duplicates (`artist+title`).
* Report missing/invalid values in `validation_report.json`.

---

## 3) Outputs

### 3.1 `songbook.md`

* Structure:

  * `# Songbook – Live Karaoke Paris`
  * For each category (in `categories.txt` order, with `Uncategorized` last):

    * `## {Category}`
    * For each artist (A→Z): `### {Artist}`

      * For each song (A→Z): `- {Title}`

### 3.2 Data artifacts for the client (JSON)

* **`songbook.json`** (normalized data, consumed by the HTML):

  ```jsonc
  {
    "meta": { "generated_at": "2025-09-19T18:00:00Z", "version": 1 },
    "categories": ["Rock","Pop","R&B/Funk","Jazz/Swing","Disco/Dance","Latin","Italian","Musicals & Standards","Uncategorized"],
    "artists": [
      { "id":"artist:madonna", "name":"Madonna", "slug":"madonna" },
      { "id":"artist:ac-dc", "name":"AC/DC", "slug":"ac-dc" }
    ],
    "songs": [
      {
        "id":"song:madonna:like-a-prayer",
        "title":"Like a Prayer",
        "artist_id":"artist:madonna",
        "artist":"Madonna",
        "category":"Pop"
      }
    ]
  }
  ```

  * Deterministic `id`/`slug` generation (lowercase, ASCII, hyphens; keep `artist` field for display).
  * `artists` lets the UI group quickly without re‑scanning all songs.
* **`search_index.json`** (tiny, precomputed search helpers):

  ```jsonc
  {
    "artists": [
      { "id":"artist:madonna", "n":"madonna", "t3":["## 4) Repository structure
  ```

```
/ (root)
├─ data/
│  ├─ karaoke_song_list.json
│  ├─ to_review.json
│  └─ categories.txt
├─ scripts/
│  ├─ build.py              # minimal: validate + normalize → emits JSON artifacts
│  ├─ lib_normalize.py      # load/normalize data; generate ids/slugs
│  ├─ lib_validate.py       # validations & report
│  └─ lib_render.py         # render MD only (site is client-driven)
├─ dist/                    # generated artifacts served by Pages
│  ├─ songbook.json         # normalized dataset for the client
│  ├─ search_index.json     # compact fuzzy index for client search
│  ├─ songbook.md           # internal reading
│  └─ index.html            # client loads JSON at runtime
├─ .github/workflows/
│  └─ build.yml             # CI: validate, build JSON, publish dist/ (Pages)
├─ README.md                # quick start guide
└─ SPEC.md                  # this document
```

```
],
"songs": [
  { "id":"song:madonna:like-a-prayer", "n":"like a prayer madonna", "t3":["lik","ike","kea", "pra", "ray", "aye", "yer", "mad", "ado" ] }
]
```

}

```
- `n` = normalized text (lowercase, diacritics stripped, punctuation removed).
- `t3` = trigram set for fast overlap scoring in the browser.
- Keep this file **small**; recompute on build.

### 3.3 `index.html`
- **Dark minimal design** with embedded CSS (no frameworks).
- Header with title, subtitle, and a **single search box** that powers both filtering and suggestions.
- One accordion `<details>` per **Category**.
- Each item: `Title — Artist` (Category shown in header). No lyrics links in v1.
- Client code **fetches** `songbook.json` and `search_index.json` from the same origin (works on GitHub Pages).
- Fallback: if `fetch` fails (offline), check for an embedded `<script type="application/json" id="songbook">…</script>`.
- Lightweight JS (~150–200 LoC total including fuzzy scoring & UI wiring).
- Accessibility: labels on search input, descriptive summaries, ARIA roles for suggestion listbox.

---

## 4) Repository structure

```

/ (root)
├─ data/
│  ├─ karaoke\_song\_list.json
│  ├─ to\_review\.json
│  └─ categories.txt
├─ scripts/
│  ├─ build.py              # entry point: generate songbook.md & index.html
│  ├─ lib\_normalize.py      # load/normalize data
│  ├─ lib\_validate.py       # validations & report
│  └─ lib\_render.py         # render MD & HTML
├─ dist/                    # generated artifacts
│  ├─ songbook.md
│  └─ index.html
├─ .github/workflows/
│  └─ build.yml             # CI: validate & publish dist/ (Pages)
├─ README.md                # quick start guide
└─ SPEC.md                  # this document

````

---

## 5) CLI commands

- **Full build** (validate + normalize + emit JSON + MD)
  ```bash
  python3 scripts/build.py --input data/karaoke_song_list.json \
                           --review data/to_review.json \
                           --categories data/categories.txt \
                           --out dist/
````

* **Validate only**

  ```bash
  python3 scripts/build.py --check-only
  ```
* **Options**

  * `--fail-on-error` → exit code ≠0 if critical errors.
  * `--include-review` → include ready songs from `to_review.json` (default: on).
  * `--emit-embedded` → also write `index-embedded.html` with inline `<script type="application/json">` fallback payloads.
  * `--sort locale=en` → locale-aware sorting; fallback ASCII lowercase.

---

## 6) Acceptance criteria (MVP)

* [ ] `songbook.json` and `search_index.json` are generated and consumed by `index.html` at runtime (no server required).
* [ ] `songbook.md` generated sorted **Category → Artist → Title**.
* [ ] `index.html` shows accordions per category; live search works; fuzzy suggestions behave as specified (typos & non‑prefix).
* [ ] Validation generates `validation_report.json` with clear warnings/errors.
* [ ] `categories.txt` controls category order in UI.
* [ ] Build reproducible locally and in CI; works on GitHub Pages (same‑origin fetch).

---

## 7) CI/CD and Deploy

* **GitHub Actions** (`.github/workflows/build.yml`):

  * Steps: checkout → setup Python → install deps → run `build.py` → publish `dist/` to GitHub Pages.
  * Artifacts: `songbook.md`, `index.html`, `validation_report.json`.
* **GitHub Pages**: serve `dist/index.html` as public root.

---

## 8) Roadmap (future versions)

### 8.1 UX/Discovery

* A–Z artist index with anchor links.
* Toggle **“Only with lyrics”**.
* Counters per category and per artist.
* **Print mode** (CSS `@media print`).

### 8.2 Data/Editing

* `songs lint --fix` script to auto-fix casing, spacing, normalize categories.
* Fuzzy duplicate detection (*Beyoncé* vs *Beyonce*, parentheses variants).
* Category synonyms module (e.g. `"Latino" → "Latin"`).

### 8.3 Site

* Persist accordion/search state in `localStorage`.
* **I18N** (EN/ES/FR) with separated strings.
* Basic analytics (clicks, searches) without cookies.
* **PWA** (installable/offline) caching `index.html` and a normalized `songbook.json`.

### 8.4 Lyrics integration

* First: allow adding `lyrics_url` fields linking to external pages.
* Later: build a **lyrics database** with clean consistent format.
* Possible API exploration (e.g. Genius, Musixmatch) to auto-fetch lyrics.

### 8.5 Productivity

* Generate **setlists** (select songs, export MD/PDF).
* Copy-to-clipboard button for artist/song lists.
* Export JSON → **CSV**.

### 8.6 Quality

* Unit tests for normalization/validation.
* End-to-end test for `index.html` (render + search).

---

## 9) Technical details

* **Category order**: if `categories.txt` missing, fallback to default; otherwise use its order + append `Uncategorized` if needed.
* **IDs/Slugs**: deterministic, lowercase ASCII, hyphen‑separated; keep original display names for UI.
* **Sorting**: use locale comparator if available; fallback to `.lower()` ASCII.
* **Fuzzy scoring** (no external deps in v1):

  * Normalize inputs: lowercase, **strip diacritics**, collapse whitespace, remove punctuation.
  * Combined score = trigram Jaccard + Damerau–Levenshtein + substring boost. Top‑N per bucket.
  * Precompute normalized names and trigrams in `search_index.json` for speed.
* **Client data loading**:

  * `index.html` uses `fetch('./songbook.json')` and `fetch('./search_index.json')` (same origin → OK on Pages).
  * Fallback `index-embedded.html` includes `<script type="application/json" id="songbook">…</script>` and similar for offline demos.
* **Lyrics (future)**: first accept `lyrics_url` (external). Later, add `lyrics/` folder with `{song_id}.html` or `{song_id}.md` to serve from Pages; index will point internally.
* **Accessibility**: `aria-label` on search; listbox semantics for suggestions; high contrast.
* **Performance**: dist JSON should remain small (artists+songs text only). Good for up to 5–10k songs; consider lazy rendering by category if nee
