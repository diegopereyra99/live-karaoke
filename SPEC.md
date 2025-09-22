# Live Karaoke Paris — Songbook (Frontend SPEC v1.1)

## 0) Goal
A **static, beautiful, and fast** website that:
- Loads data from `songbook.json` and `search_index.json`.
- Displays accordions by **Category → Artist → Song**.
- Provides **fuzzy search** tolerant to typos.
- Default **dark mode**, automatic light mode via `prefers-color-scheme`.
- Fully **accessible and keyboard-navigable**.
- No frameworks; plain HTML/CSS/JS only.

---

## 1) File Structure (dist/)
```
/dist
index.html # SPA estática
styles.css # Design system + componentes
app.js # Lógica UI + search + render
songbook.json # Datos normalizados
search_index.json # Índice precomputado para fuzzy
assets/
logo.svg
icons.svg # sprite de íconos accesibles
preview.png
```


> **No** external dependencies (CDN). Must work standalone (GitHub Pages/Netlify).

---

## 2) Design System (mandatory tokens)

### 2.1 Colors
- Dark by default, light overrides with `prefers-color-scheme`.
- Tokens:  
  - `--bg`, `--panel`, `--text`, `--muted`, `--subtle`  
  - `--accent`, `--accent-2`, `--danger`, `--ring`, `--shadow`

### 2.2 Typography
- Stack: `Inter, Segoe UI, system-ui, -apple-system, Roboto, Ubuntu, Arial, sans-serif`
- Headings 700–800, text 400–500
- Line-height: 1.35

### 2.3 Spacing & Radius
- Scale: `--space-1` = 4px … `--space-6` = 24px
- Radii: `--radius`, `--radius-sm`, `--radius-xs`

### 2.4 States
- Hover: subtle shadow + lift  
- Focus: 2px visible ring  
- Active: compress by 1px  
- Transitions: 150–220ms cubic-bezier(.2,.8,.2,1)

---

## 3) Layout & Components

### 3.1 Header
- Logo + title + search bar
- Sticky + blur + bottom border
- `role="banner"`

### 3.2 Search
- `<input type="search">` with live fuzzy search
- Suggestions in an accessible listbox
- Keyboard navigation with ↑/↓/Enter/Escape
- On confirm → expand accordion + scroll + highlight song

### 3.3 Accordions
- Categories → Artists → Songs
- Counts at each level
- State persisted via SessionStorage
- Smooth height animation
- Songs clickable with hover/active states

### 3.4 States
- Loading skeleton  
- Empty search → “No matches…”  
- Fetch error → Retry button

### 3.5 Footer
- Data version + build date

---

## 4) Behavior

- Load JSON with fetch + retry  
- Schema validation (categories → artists → songs)  
- Sorting via `Intl.Collator`  
- Fuzzy search (substring + trigram + Damerau-Levenshtein)  
- Ranking: top 50 internal, top 8 displayed  

---

## 5) Accessibility
- Focus visible everywhere  
- `aria-expanded`, `aria-controls` for accordions  
- Accessible listbox for search  
- Contrast ratio ≥ 4.5:1  
- Respect `prefers-reduced-motion`

---

## 6) Acceptance Checklist

- [ ] JSON loads and renders correctly  
- [ ] Correct counts for categories/artists  
- [ ] Fuzzy search works with typos  
- [ ] Fully navigable by keyboard and mouse  
- [ ] Dark mode default / light mode via system  
- [ ] Visible focus ring on all elements  
- [ ] Meets WCAG AA contrast requirements  
- [ ] Closed categories do not mount DOM children

---

## 7) Reject PR if…
- Adds unapproved frameworks  
- Injects inline styles in JS  
- Breaks dark/light mode  
- Removes focus visibility  
- Does not implement accordions or search correctly

---

## 8) Roadmap (v1.2+)
- Add `lyrics_url` links  
- “Copy link” with hash anchors (`#cat/artist/song`)  
- i18n (EN/ES/FR) via string file  
- Optional filter tags (decade/language)
