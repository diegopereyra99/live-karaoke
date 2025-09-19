from __future__ import annotations

from collections import defaultdict
from typing import Any


def render_markdown(dataset: dict[str, Any], categories_order: list[str]) -> str:
    # Group by category -> artist
    by_cat_artist: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for s in dataset.get("songs", []):
        cat = s.get("category") or "Uncategorized"
        artist = s.get("artist") or "Unknown"
        by_cat_artist[cat][artist].append(s)

    # Ensure deterministic order inside groups
    for cat in by_cat_artist:
        for artist in by_cat_artist[cat]:
            by_cat_artist[cat][artist].sort(key=lambda x: (x.get("title") or ""))

    lines: list[str] = []
    lines.append("# Songbook – Live Karaoke Paris")

    # Categories: in provided order, then any extras, with 'Uncategorized' last
    extras = [c for c in by_cat_artist.keys() if c not in categories_order and c != "Uncategorized"]
    ordered_cats = list(categories_order) + sorted(extras)
    if "Uncategorized" not in ordered_cats and "Uncategorized" in by_cat_artist:
        ordered_cats.append("Uncategorized")

    for cat in ordered_cats:
        artists_map = by_cat_artist.get(cat)
        if not artists_map:
            continue
        lines.append("")
        lines.append(f"## {cat}")
        for artist in sorted(artists_map.keys()):
            lines.append("")
            lines.append(f"### {artist}")
            for song in artists_map[artist]:
                lines.append(f"- {song.get('title','')}")

    lines.append("")
    return "\n".join(lines)


def render_index_html(dataset: dict[str, Any]) -> str:
    # Client-driven UI: we ship a minimal shell that fetches songbook.json
    # and renders one accordion per category, with items as "Title — Artist".
    html = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Live Karaoke Paris — Songbook</title>
  <style>
    :root {{
      --bg: #0f1115;
      --panel: #171a21;
      --text: #e6ebf1;
      --muted: #9aa5b1;
      --accent: #7aa2f7;
      --border: #2a2f3a;
      --highlight: #2b3b6b;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; }}
    header {{ padding: 20px 16px; max-width: 900px; margin: 0 auto; }}
    h1 {{ margin: 0 0 6px; font-size: 1.6rem; font-weight: 650; }}
    p.subtitle {{ margin: 0; color: var(--muted); }}
    .search {{ margin-top: 14px; display: flex; gap: 10px; align-items: center; }}
    .search label {{ font-size: 0.9rem; color: var(--muted); }}
    .search input {{ flex: 1; padding: 10px 12px; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; color: var(--text); outline: none; }}
    .search input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(122,162,247,0.15); }}
    main {{ max-width: 900px; margin: 8px auto 40px; padding: 0 16px; }}
    details {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; margin: 10px 0; overflow: hidden; }}
    summary {{ list-style: none; cursor: pointer; padding: 12px 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
    summary::-webkit-details-marker {{ display: none; }}
    summary .count {{ color: var(--muted); font-weight: 500; font-size: 0.9rem; }}
    ul.songs {{ margin: 0; padding: 8px 0 12px; }}
    li.song {{ display: flex; gap: 8px; align-items: baseline; padding: 6px 14px; border-top: 1px solid var(--border); }}
    li.song:hover {{ background: var(--highlight); }}
    .title {{ font-weight: 600; }}
    .dash {{ color: var(--muted); margin: 0 4px; }}
    .artist {{ color: var(--muted); font-weight: 500; }}
    .visually-hidden {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }}
    .no-results {{ color: var(--muted); padding: 12px 6px 0; }}
  </style>
</head>
<body>
  <header>
    <h1>Live Karaoke Paris — Songbook</h1>
    <p class=\"subtitle\">Browse by category or search title/artist.</p>
    <div class=\"search\">
      <label for=\"q\">Search</label>
      <input id=\"q\" type=\"search\" placeholder=\"Type to filter…\" autocomplete=\"off\" spellcheck=\"false\" />
    </div>
  </header>
  <main id=\"app\" aria-live=\"polite\"></main>
  <script>
  (function() {{
    const app = document.getElementById('app');
    const input = document.getElementById('q');

    const norm = (s) => (s || '').normalize('NFKD').replace(/\p{Diacritic}+/gu,'').toLowerCase();
    function render(data) {{
      const q = norm(input.value);
      const cats = data.categories;
      const songs = data.songs;

      const byCat = new Map(cats.map(c => [c, []]));
      for (const s of songs) {{
        const hay = norm(s.title + ' ' + (s.artist || '') + ' ' + (s.category || ''));
        if (q && !hay.includes(q)) continue;
        const c = byCat.has(s.category) ? s.category : 'Uncategorized';
        byCat.get(c).push(s);
      }}

      app.innerHTML = '';
      let any = false;
      for (const c of cats) {{
        const list = byCat.get(c) || [];
        if (!list.length) continue;
        any = true;
        const details = document.createElement('details');
        const summary = document.createElement('summary');
        summary.innerHTML = `<span>${c}</span> <span class="count">(${list.length})</span>`;
        details.appendChild(summary);

        const ul = document.createElement('ul');
        ul.className = 'songs';
        for (const s of list) {{
          const li = document.createElement('li');
          li.className = 'song';
          li.innerHTML = `<span class="title">${s.title}</span><span class="dash">—</span><span class="artist">${s.artist || ''}</span>`;
          ul.appendChild(li);
        }}
        details.appendChild(ul);
        app.appendChild(details);
      }}

      if (!any) {{
        const p = document.createElement('p');
        p.className = 'no-results';
        p.textContent = 'No matches.';
        app.appendChild(p);
      }}
    }}

    async function boot() {{
      try {{
        const res = await fetch('./songbook.json', { cache: 'no-store' });
        if (!res.ok) throw new Error('fetch failed');
        const data = await res.json();
        window.__DATA__ = data;
        render(data);
        input.addEventListener('input', () => render(data));
      }} catch (e) {{
        // Fallback: if an embedded JSON script exists, use it
        const tag = document.getElementById('songbook');
        if (tag) {{
          try {{
            const data = JSON.parse(tag.textContent || '{}');
            window.__DATA__ = data;
            render(data);
            input.addEventListener('input', () => render(data));
            return;
          }} catch {{}}
        }}
        app.innerHTML = '<p class="no-results">Could not load data.</p>';
      }}
    }}
    boot();
  }})();
  </script>
</body>
</html>
"""
    return html
