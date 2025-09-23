// app.js — Suggestions UX improvements + stricter fuzzy search (vanilla JS)

(function () {
  // Progressive background image load (vinyls)
  (function preloadBg(){
    try {
      const prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const srcWebp = './assets/vinyls-cool.webp';
      const srcPng = './assets/vinyls-cool.png';
      const img = new Image();
      img.onload = function(){ document.body.classList.add('bg-ready'); };
      img.onerror = function(){
        const fallback = new Image();
        fallback.onload = function(){ document.body.classList.add('bg-ready'); };
        fallback.src = srcPng;
      };
      img.src = srcWebp;
      // If motion is reduced, apply ready state sooner to avoid long animations
      if (prefersReduced) document.body.classList.add('bg-ready');
    } catch {}
  })();
  // Elements (support both current ids and legacy ones)
  const app = document.getElementById('app');
  const meta = document.getElementById('build-meta');
  const search = document.getElementById('search') || document.getElementById('q');
  const panel = document.getElementById('search-panel') || document.getElementById('suggestions');

  const collator = new Intl.Collator(undefined, { sensitivity: 'base' });

  // Session: open categories
  const OPEN_KEY = 'lkp_open_cats_v2';
  function getOpenSet() { try { return new Set(JSON.parse(sessionStorage.getItem(OPEN_KEY) || '[]')); } catch { return new Set(); } }
  function saveOpenSet(set) { try { sessionStorage.setItem(OPEN_KEY, JSON.stringify(Array.from(set))); } catch {} }

  // Helpers
  function clear(el) { while (el && el.firstChild) el.removeChild(el.firstChild); }
  async function fetchWithRetry(url, tries = 2) { let last; for (let i=0;i<tries;i++){ try{ const r=await fetch(url,{cache:'no-store'}); if(!r.ok) throw new Error('HTTP '+r.status); return await r.json(); } catch(e){ last=e; } } throw last||new Error('Failed'); }

  // Render main accordion (Category → Artist → Songs)
  function render(data) {
    const cats = data.categories || [];
    const songs = data.songs || [];
    const byCat = new Map(cats.map((c) => [c, new Map()]));
    for (const s of songs) {
      const scats = Array.isArray(s.categories) && s.categories.length ? s.categories : (s.category ? [s.category] : ['Uncategorized']);
      for (const rawCat of scats) {
        const cat = byCat.has(rawCat) ? rawCat : 'Uncategorized';
        const artist = s.artist || 'Unknown';
        if (!byCat.get(cat).has(artist)) byCat.get(cat).set(artist, []);
        byCat.get(cat).get(artist).push(s);
      }
    }
    for (const [, amap] of byCat) for (const [, arr] of amap) arr.sort((x,y)=>collator.compare(x.title||'', y.title||''));

    clear(app);
    const openSet = getOpenSet();

    // All Songs panel (artist → songs across all categories)
    const byArtist = new Map();
    for (const s of songs) {
      const artist = s.artist || 'Unknown';
      if (!byArtist.has(artist)) byArtist.set(artist, []);
      byArtist.get(artist).push(s);
    }
    for (const [, arr] of byArtist) arr.sort((x,y)=>collator.compare(x.title||'', y.title||''));
    if (byArtist.size) {
      const details = document.createElement('details'); details.className='panel'; details.id = 'all-songs';
      const hasPref = sessionStorage.getItem(OPEN_KEY) != null;
      details.open = openSet.has('__ALL__'); // default closed if no preference
      const totalSongs = songs.length;
      const totalArtists = byArtist.size;
      const summary = document.createElement('summary'); summary.className='summary'; summary.setAttribute('aria-controls','sect-all'); summary.setAttribute('aria-expanded',String(details.open)); summary.textContent = 'All Songs';
      details.appendChild(summary);
      const mountChildren = () => {
        if (details.querySelector('ul.songs')) return;
        const artists=Array.from(byArtist.keys()).sort(collator.compare);
        for(const artist of artists){
          const list=byArtist.get(artist)||[];
          const ul=document.createElement('ul'); ul.className='songs';
          const ah=document.createElement('li'); ah.className='artist-header'; ah.textContent=`${artist}`; ul.appendChild(ah);
          for(const s of list){
            const li=document.createElement('li');
            li.className='song-item';
            li.dataset.songId=s.id;
            const primary = s.lyrics_url || '';
            const fallback = s.fallback_url || '';
            const href = primary || fallback || '#';
            const titleHtml = (href && href !== '#')
              ? `<a class="song-link" href="${href}" target="_blank" rel="noopener noreferrer">${s.title}</a>`
              : `${s.title}`;
            li.innerHTML = `${titleHtml}`;
            ul.appendChild(li);
          }
          details.appendChild(ul);
        }
      };
      const unmountChildren = () => { for (const ul of details.querySelectorAll('ul.songs')) ul.remove(); };
      details.addEventListener('toggle',()=>{ summary.setAttribute('aria-expanded',String(details.open)); const set=getOpenSet(); if(details.open){ set.add('__ALL__'); saveOpenSet(set); mountChildren(); } else { set.delete('__ALL__'); saveOpenSet(set); unmountChildren(); } });
      if (details.open) mountChildren();
      app.appendChild(details);
    }
    for (const [cat, artistMap] of byCat) {
      const count = Array.from(artistMap.values()).reduce((n, arr) => n + arr.length, 0);
      if (!count) continue;
      const details = document.createElement('details'); details.className='panel'; details.open = openSet.has(cat);
      const summary = document.createElement('summary'); summary.className='summary'; summary.setAttribute('aria-controls',`sect-${cat}`); summary.setAttribute('aria-expanded',String(details.open)); summary.textContent = `${cat}`; details.appendChild(summary);
      const mountChildren = () => { if (details.querySelector('ul.songs')) return; const artists=Array.from(artistMap.keys()).sort(collator.compare); for(const artist of artists){ const list=artistMap.get(artist)||[]; const ul=document.createElement('ul'); ul.className='songs'; const ah=document.createElement('li'); ah.className='artist-header'; ah.textContent=`${artist}`; ul.appendChild(ah); for(const s of list){ const li=document.createElement('li'); li.className='song-item'; li.dataset.songId=s.id; const primary=s.lyrics_url||''; const fallback=s.fallback_url||''; const href=primary||fallback||'#'; const titleHtml = (href && href !== '#') ? `<a class=\"song-link\" href=\"${href}\" target=\"_blank\" rel=\"noopener noreferrer\">${s.title}</a>` : `${s.title}`; li.innerHTML = `${titleHtml}`; ul.appendChild(li);} details.appendChild(ul);} };
      const unmountChildren = () => { for (const ul of details.querySelectorAll('ul.songs')) ul.remove(); };
      details.addEventListener('toggle',()=>{ summary.setAttribute('aria-expanded',String(details.open)); const set=getOpenSet(); if(details.open){ set.add(cat); saveOpenSet(set); mountChildren(); } else { set.delete(cat); saveOpenSet(set); unmountChildren(); } });
      if (details.open) mountChildren();
      app.appendChild(details);
    }
    if (!app.children.length) { const p=document.createElement('p'); p.className='no-results'; p.textContent='No matches.'; app.appendChild(p); }
  }

  // Navigate to song id and highlight (3s)
  function choose(songId) {
    closePanel();
    if (!window.__DATA__) return;
    const s = window.__DATA__.songs.find(x=>x.id===songId); if(!s) return;
    const detailsList = Array.from(app.querySelectorAll('details.panel'));
    const scats = Array.isArray(s.categories) && s.categories.length ? s.categories : (s.category ? [s.category] : ['Uncategorized']);
    const preferred = scats[0] || 'Uncategorized';
    const target = detailsList.find(d => d.querySelector('summary')?.textContent?.startsWith(preferred));
    if (!target) return; if (!target.open) target.open = true;
    requestAnimationFrame(()=>{ const el=app.querySelector(`li.song-item[data-song-id="${CSS.escape(songId)}"]`); if(el){ el.scrollIntoView({behavior:'smooth', block:'center'}); el.classList.add('highlight'); setTimeout(()=>el.classList.remove('highlight'), 3000); } });
  }

  // Navigate to artist: open a category containing the artist and scroll to its header
  function chooseArtist(artistName){
    closePanel();
    const data = window.__DATA__;
    if(!data) return;
    const songs = (data.songs||[]).filter(s => (s.artist||'') === artistName);
    if(!songs.length) return;
    const scats = Array.isArray(songs[0].categories) && songs[0].categories.length ? songs[0].categories : (songs[0].category ? [songs[0].category] : ['Uncategorized']);
    const category = scats[0] || 'Uncategorized';
    const detailsList = Array.from(app.querySelectorAll('details.panel'));
    const target = detailsList.find(d => d.querySelector('summary')?.textContent?.startsWith(category));
    if(!target) return;
    if(!target.open) target.open = true;
    requestAnimationFrame(()=>{
      const headers = Array.from(target.querySelectorAll('li.artist-header'));
      const el = headers.find(h => (h.textContent||'').trim() === artistName);
      if(el){ el.scrollIntoView({behavior:'smooth', block:'start'}); el.classList.add('highlight'); setTimeout(()=>el.classList.remove('highlight'), 3000); }
    });
  }

  // ===== Suggestions panel UX =====
  let activeIndex = -1;         // Keyboard index
  let currentResults = [];      // Rendered results
  let ignoreBlur = false;       // Prevent close on blur when clicking panel

  function openPanel() { panel.hidden = false; search?.setAttribute('aria-expanded','true'); }
  function closePanel() { panel.hidden = true; search?.setAttribute('aria-expanded','false'); activeIndex=-1; search?.removeAttribute('aria-activedescendant'); }
  function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }

  // ===== Stricter fuzzy search =====
  function norm(s){ s=(s||'').normalize('NFKD').replace(/\p{Diacritic}+/gu,''); s=s.toLowerCase().replace(/[^a-z0-9\s]+/g,' '); return s.replace(/\s+/g,' ').trim(); }
  function trigrams(s){ const t=`  ${s}  `; const a=[]; for(let i=0;i<t.length-2;i++) a.push(t.slice(i,i+3)); return Array.from(new Set(a)); }
  function jaccard(a,b){ const A=new Set(a),B=new Set(b); let inter=0; for(const x of A) if(B.has(x)) inter++; const uni=A.size+B.size-inter||1; return inter/uni; }
  function dlev(a,b){ const al=a.length, bl=b.length; if(!al) return bl; if(!bl) return al; const dp=Array.from({length:al+1},()=>new Array(bl+1).fill(0)); for(let i=0;i<=al;i++) dp[i][0]=i; for(let j=0;j<=bl;j++) dp[0][j]=j; for(let i=1;i<=al;i++){ for(let j=1;j<=bl;j++){ const cost=a[i-1]===b[j-1]?0:1; dp[i][j]=Math.min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost); if(i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1]) dp[i][j]=Math.min(dp[i][j], dp[i-2][j-2]+cost); } } return dp[al][bl]; }
  function passesHardFilter(q,t){ const nq=norm(q), nt=norm(t); const L=nq.length; if(L===0||nt.length===0) return false; const substr=nt.includes(nq); const tj=jaccard(trigrams(nq), trigrams(nt)); const edn=1 - dlev(nq,nt)/Math.max(nq.length, nt.length); if(L<=3) return substr||tj>=0.60||edn>=0.85; if(L<=6) return substr||tj>=0.45||edn>=0.80; return substr||tj>=0.40||edn>=0.78; }
  function scoreHit(q,t){ const nq=norm(q), nt=norm(t); const substr=nt.includes(nq)?1:0; const tj=jaccard(trigrams(nq), trigrams(nt)); const edn=1 - dlev(nq,nt)/Math.max(nq.length, nt.length); return substr*0.55 + tj*0.30 + edn*0.15; }

  function findTitle(id){ const s=(window.__DATA__?.songs||[]).find(x=>x.id===id); return s?.title||''; }
  function findArtist(id){ const s=(window.__DATA__?.songs||[]).find(x=>x.id===id); return s?.artist||''; }
  function getSongItems(){ if(window.__INDEX__ && Array.isArray(window.__INDEX__.songs)){ return window.__INDEX__.songs.map(s=>({ type:'song', id:s.id, label:`${(findTitle(s.id)||'').trim()} — ${(findArtist(s.id)||'').trim()}`, value: norm(`${s.t||''} ${s.a||''} ${s.c||''}`) })); } const out=[]; for(const s of (window.__DATA__?.songs||[])){ const cats = Array.isArray(s.categories)? s.categories.join(' ') : (s.category||''); out.push({ type:'song', id:s.id, label:`${s.title||''} — ${s.artist||''}`, value: norm(`${s.title||''} ${s.artist||''} ${cats}`) }); } return out; }
  function getArtistItems(){ const seen=new Set(); const items=[]; for(const s of (window.__DATA__?.songs||[])){ const a=(s.artist||'').trim(); if(!a||seen.has(a)) continue; seen.add(a); items.push({ type:'artist', artist:a, label:a, value:norm(a) }); } return items; }
  function searchHits(query, items){ const nq=norm(query); if(!nq) return []; const arr=[]; for(const it of items){ const text=it.value||norm(it.label||''); if(!passesHardFilter(nq, text)) continue; const score=scoreHit(nq, text); arr.push({...it, score}); } arr.sort((a,b)=>b.score-a.score); return arr; }

  function renderPanel(results){ currentResults=results; clear(panel); if(!results.length) return; const box=document.createElement('div'); box.className='panel'; const list=document.createElement('div'); list.className='list'; list.setAttribute('role','listbox'); results.forEach((r,i)=>{ const opt=document.createElement('div'); opt.className='item'; opt.setAttribute('role','option'); opt.id=`opt-${i}`; opt.dataset.index=String(i); if(r.type==='artist'){ opt.dataset.kind='artist'; opt.textContent=r.label||''; } else { opt.dataset.kind='song'; opt.dataset.id=r.id||''; opt.textContent=r.label||''; } list.appendChild(opt); }); box.appendChild(list); panel.appendChild(box); setActive(0); }
  function setActive(i){ const list=panel.querySelector('[role="listbox"]'); if(!list) return; const items=Array.from(list.querySelectorAll('[role="option"]')); if(!items.length) return; activeIndex=Math.max(0, Math.min(i, items.length-1)); items.forEach((el,idx)=>{ el.setAttribute('aria-selected', String(idx===activeIndex)); el.classList.toggle('active', idx===activeIndex); }); const activeEl=items[activeIndex]; if(activeEl) search?.setAttribute('aria-activedescendant', activeEl.id); }

  // Handlers
  function onKeydown(e){ // Arrows/Enter/Escape on input
    if(e.key==='Escape'){ closePanel(); return; }
    if(panel.hidden) return;
    if(e.key==='ArrowDown'){ e.preventDefault(); setActive(activeIndex+1); }
    else if(e.key==='ArrowUp'){ e.preventDefault(); setActive(activeIndex-1); }
    else if(e.key==='Enter'){ e.preventDefault(); const hit=currentResults[activeIndex]; if(!hit) return; if(hit.type==='artist'){ chooseArtist(hit.artist); } else { choose(hit.id); } closePanel(); }
  }
  function onSelectSuggestion(e){ // Click on a suggestion
    const opt=e.target.closest('[role="option"][data-index]'); if(!opt) return; const hit=currentResults[Number(opt.dataset.index)]; if(!hit) return; if(hit.type==='artist'){ chooseArtist(hit.artist); } else { choose(hit.id); } closePanel(); }
  function onPanelPointerDown(){ // Keep open through click
    ignoreBlur = true;
  }
  function onBlur(){ // Close panel after blur (allow click)
    setTimeout(()=>{ if(ignoreBlur){ ignoreBlur=false; return; } closePanel(); }, 0);
  }
  function closeIfOutside(e){ // Close on click/tap outside
    const t=e.target; if(t===search || panel.contains(t) || search.contains(t)) return; closePanel();
  }
  const runSearch = debounce(()=>{ const q=search.value||''; if(q.trim().length===0){ clear(panel); currentResults=[]; closePanel(); return; } const arts=searchHits(q, getArtistItems()); const songs=searchHits(q, getSongItems()); const combined=[...arts.slice(0,5), ...songs.slice(0, Math.max(0, 8-arts.slice(0,5).length))]; if(!combined.length){ clear(panel); closePanel(); return; } renderPanel(combined); openPanel(); }, 140);

  // Boot
  async function boot(){
    app.innerHTML = '<p class="no-results">Loading…</p>';
    try {
      const [data, index] = await Promise.all([
        fetchWithRetry('./songbook.json', 2),
        fetchWithRetry('./search_index.json', 2)
      ]);
      window.__DATA__ = data; window.__INDEX__ = index;
      render(data);

      if (search && panel) {
        search.setAttribute('aria-haspopup','listbox'); search.setAttribute('aria-expanded','false');
        search.addEventListener('keydown', onKeydown);
        search.addEventListener('blur', onBlur);
        search.addEventListener('input', runSearch);
        panel.addEventListener('click', onSelectSuggestion);
        panel.addEventListener('pointerdown', onPanelPointerDown);
        window.addEventListener('scroll', closePanel, { passive: true });
        document.addEventListener('pointerdown', closeIfOutside);
      }
    } catch (e) {
      app.innerHTML = '<p class="no-results">Could not load data. <button id="retry">Retry</button></p>';
      if (meta) meta.textContent = '';
      const btn=document.getElementById('retry'); if(btn) btn.addEventListener('click', boot);
    }
  }

  boot();
})();
