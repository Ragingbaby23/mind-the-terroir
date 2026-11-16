# generate.py - Mind the Terroir (v2.0)
# Baca data/beans.json + data/green_beans.json -> tulis site/index.html
# Baru v2.0: dua SECTION TERPISAH (Roasted / Green) + filter & sort katalog.
# Tetap cuma konsep level kita: dict, list, for, f-string.

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # naik 1 folder = folder project
data = json.loads((ROOT / "data" / "beans.json").read_text(encoding="utf-8"))
beans = data["beans"]
green = []
green_path = ROOT / "data" / "green_beans.json"
if green_path.exists():
    green = json.loads(green_path.read_text(encoding="utf-8"))["lots"]

# Kurs KIRA-KIRA, cuma buat urutan tampil di sort harga (bukan harga asli).
RATE_TO_USD = {"USD": 1.0, "EUR": 1.08, "AED": 0.2723}

def esc(s):                                          # escape biar nama pakai ' atau & nggak merusak HTML
    return html.escape(str(s), quote=True)

CSS = """
:root { --bg:#171310; --card:#211b16; --line:#3a2f26; --ink:#efe7dc; --mut:#a89a8a; --acc:#d9a05b; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; }
header { padding:40px 20px 12px; text-align:center; }
h1 { margin:0; font-size:2rem; letter-spacing:.5px; }
h1 span { color:var(--acc); }
.tag { color:var(--mut); margin:6px 0 18px; }
#q { width:min(520px,90%); padding:10px 14px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink); font-size:1rem; }
#controls { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; padding:14px 20px 4px; max-width:1100px; margin:0 auto; }
#controls select { padding:8px 10px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink); font-size:.9rem; max-width:240px; }
.meta { color:var(--mut); font-size:.85rem; margin:10px 0 0; }
section.sec { max-width:1100px; margin:0 auto; padding:0 24px; }
.sec-head { display:flex; flex-wrap:wrap; align-items:baseline; gap:10px; border-top:2px solid var(--line); margin-top:28px; padding-top:18px; }
.sec-head h2 { margin:0; font-size:1.35rem; letter-spacing:.5px; }
.sec-head h2 em { color:var(--acc); font-style:normal; }
.sec-head .sub { color:var(--mut); font-size:.85rem; }
.sec-count { color:var(--acc); font-weight:700; font-size:1rem; }
.grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; padding:14px 0 26px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; display:flex; flex-direction:column; gap:6px; }
.card h2 { margin:0; font-size:1.05rem; }
.roaster { color:var(--acc); margin:0; font-size:.85rem; }
.proc { color:var(--mut); margin:0; font-size:.85rem; }
.card img.pic { width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:10px; margin-bottom:8px; background:var(--line); }
.notes { margin:4px 0; font-style:italic; }
.price { margin:auto 0 0; font-weight:600; }
a { color:var(--acc); text-decoration:none; font-size:.9rem; }
.badge { font-size:.7rem; border-radius:6px; padding:2px 6px; vertical-align:middle; margin-left:6px; }
.badge.new { background:#2e4a2e; color:#9fd99f; }
.badge.out { background:#4a2e2e; color:#d99f9f; }
.badge.green { background:#2e444a; color:#9fd9d9; }
.score { color:#9fd99f; font-size:.8rem; font-weight:600; }
.na { color:var(--mut); font-style:italic; font-size:.8rem; }
p.contact { color:var(--mut); font-size:.85rem; margin:0; }
footer { text-align:center; color:var(--mut); padding:24px; font-size:.85rem; border-top:1px solid var(--line); }
footer a { color:var(--mut); text-decoration:underline; }
"""

JS = """
const q   = document.getElementById('q');
const fs  = document.getElementById('f-sec');
const fr  = document.getElementById('f-roaster');
const fo  = document.getElementById('f-origin');
const so  = document.getElementById('f-sort');
const cards = [...document.querySelectorAll('.card')];
const grids = {roasted: document.getElementById('grid-roasted'),
               green:   document.getElementById('grid-green')};
const countEl = document.getElementById('count');

function visible(c){
  if (fs.value !== 'all' && c.dataset.sec !== fs.value) return false;
  if (fr.value !== 'all' && c.dataset.roaster !== fr.value) return false;
  if (fo.value !== 'all' && c.dataset.origin !== fo.value) return false;
  const s = q.value.toLowerCase();
  return (c.dataset.search + ' ' + c.textContent).toLowerCase().includes(s);
}

function num(v){ return v === '' ? null : parseFloat(v); }

function sorted(list){
  const m = so.value;
  const byIdx = (a,b) => a.dataset.idx - b.dataset.idx;
  if (m === 'name')       return list.sort((a,b) => a.dataset.name.localeCompare(b.dataset.name));
  if (m === 'price-up')   return list.sort((a,b) => (num(a.dataset.price) ??  Infinity) - (num(b.dataset.price) ??  Infinity) || byIdx(a,b));
  if (m === 'price-down') return list.sort((a,b) => (num(b.dataset.price) ?? -Infinity) - (num(a.dataset.price) ?? -Infinity) || byIdx(a,b));
  if (m === 'score')      return list.sort((a,b) => (num(b.dataset.score) ?? -1) - (num(a.dataset.score) ?? -1) || byIdx(a,b));
  if (m === 'new')        return list.sort((a,b) => (b.dataset.new === '1') - (a.dataset.new === '1') || byIdx(a,b));
  return list.sort(byIdx);
}

function update(){
  let n = 0;
  for (const c of cards){
    const ok = visible(c);
    c.style.display = ok ? '' : 'none';
    if (ok) n++;
  }
  for (const sec of ['roasted','green']){
    const list = cards.filter(c => c.dataset.sec === sec && c.style.display !== 'none');
    sorted(list).forEach(c => grids[sec].appendChild(c));   // re-append = urutan grid ikut sort
    document.getElementById('sec-' + sec).style.display = list.length ? '' : 'none';
    document.getElementById('cnt-' + sec).textContent = list.length;
  }
  countEl.textContent = n + ' of ' + cards.length + ' beans';
}
[q, fs, fr, fo, so].forEach(el => el.addEventListener('input', update));
update();
"""

SYMBOL = {"USD": "$", "EUR": "€", "AED": "AED "}

def price_text(p):                                   # dict di dalam dict: p["amount"]
    sym = SYMBOL.get(p["currency"], p["currency"] + " ")
    t = f"{sym}{p['amount']:.2f}"
    return f"from {t}" if p["from"] else t

def price_usd(p):                                    # harga kira-kira dalam USD, khusus sort
    return p["amount"] * RATE_TO_USD.get(p["currency"], 1.0)

# opsi dropdown = gabungan dari kedua dataset
roasters = sorted({b["roaster"] for b in beans} | {g["roaster"] for g in green})
origins  = sorted({(b["origin"] or "Blend") for b in beans} | {(g["origin"] or "Blend") for g in green})

def options(placeholder, values):                     # placeholder = label dropdown saat 'All'
    out = f"<option value='all'>{placeholder}</option>"
    for v in values:
        out += f"<option value=\"{esc(v)}\">{esc(v)}</option>"
    return out

parts = []
parts.append(
    "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Mind the Terroir</title><style>" + CSS + "</style></head><body>"
    "<header><h1>Mind the <span>Terroir</span></h1>"
    "<p class='tag'>Fresh beans, five roasters, one place.</p>"
    "<input id='q' placeholder='Search beans, origins, notes...' autocomplete='off'>"
    "<div id='controls'>"
    "<select id='f-sec' title='Filter by section'><option value='all'>Section: all</option>"
    "<option value='roasted'>Roasted only</option><option value='green'>Green only</option></select>"
    "<select id='f-roaster' title='Filter by roaster'>" + options("Roaster: all", roasters) + "</select>"
    "<select id='f-origin' title='Filter by origin'>" + options("Origin: all", origins) + "</select>"
    "<select id='f-sort' title='Sort order'>"
    "<option value='default'>Sort: Featured</option>"
    "<option value='name'>Name A&ndash;Z</option>"
    "<option value='price-up'>Price: low &rarr; high</option>"
    "<option value='price-down'>Price: high &rarr; low</option>"
    "<option value='score'>Cupping score &darr;</option>"
    "<option value='new'>Newest first</option>"
    "</select></div>"
    "<p class='meta' id='count'></p></header>"
)

# ---------- SECTION 1: ROASTED BEANS ----------
parts.append(
    "<section class='sec' id='sec-roasted'>"
    "<div class='sec-head'><h2><em>Roasted Beans</em></h2>"
    "<span class='sec-count' id='cnt-roasted'></span>"
    "<span class='sub'>ready to brew, per roaster price</span></div>"
    "<div class='grid' id='grid-roasted'>"
)
for idx, b in enumerate(beans):                      # <- loop inti project ini
    notes = (" &bull; ".join(esc(n) for n in b["tasting_notes"])
             if b["tasting_notes"] else "&mdash;")   # escape per note, entity join belakangan
    badges = ""
    if b["is_new"]:
        badges += "<span class='badge new'>NEW</span>"
    if b["availability"] == "sold_out":
        badges += "<span class='badge out'>SOLD OUT</span>"
    search_text = b["name"] + " " + (b["origin"] or "") + " " + " ".join(b["tasting_notes"])
    img = (
        f"<img class='pic' src='{esc(b['image'])}' alt='' loading='lazy'>"
        if b.get("image") else ""
    )
    parts.append(
        f"<article class='card' data-sec='roasted' data-idx='{idx}'"
        f" data-name=\"{esc(b['name'])}\" data-roaster=\"{esc(b['roaster'])}\""
        f" data-origin=\"{esc(b['origin'] or 'Blend')}\""
        f" data-price='{price_usd(b['price']):.2f}' data-score=''"
        f" data-new='{1 if b['is_new'] else 0}'"
        f" data-search=\"{esc(search_text)}\">"
        f"{img}"
        f"<h2>{esc(b['name'])} {badges}</h2>"
        f"<p class='roaster'>{esc(b['roaster'])} &middot; {esc(b['origin'] or 'Blend')}</p>"
        f"<p class='proc'>{esc(b['process_variety'] or '')}</p>"
        f"<p class='notes'>{notes}</p>"
        f"<p class='price'>{price_text(b['price'])}</p>"
        f"<a href='{esc(b['url'])}' target='_blank'>View at roaster &rarr;</a>"
        f"</article>"
    )
parts.append("</div></section>")

# ---------- SECTION 2: GREEN BEANS (terpisah penuh) ----------
if green:
    parts.append(
        "<section class='sec' id='sec-green'>"
        "<div class='sec-head' id='green'><h2><em>Green Beans</em></h2>"
        "<span class='sec-count' id='cnt-green'></span>"
        "<span class='sub'>unroasted, priced per lb, for roasters</span></div>"
        "<div class='grid' id='grid-green'>"
    )
    for idx, g in enumerate(green):
        notes = (" &bull; ".join(esc(n) for n in g["tasting_notes"])
                 if g["tasting_notes"] else "&mdash;")
        score_val = f"{g['score']:.1f}" if g.get("score") else ""
        score = (f"<span class='score'>{score_val}</span>"
                 if g.get("score") else "<span class='na'>no score</span>")
        price = (f"${g['price_per_lb']:.2f}/lb"
                 if g.get("price_per_lb")
                 else (f"{esc(g['price_display'])}"
                       if g.get("price_display")
                       else "<p class='contact'>Contact seller for price</p>"))
        price_attr = f"{g['price_per_lb']:.2f}" if g.get("price_per_lb") else ""
        arrival = f" <span class='na'>(arr. {esc(g['arrival'])})</span>" if g.get("arrival") else ""
        search_text = " ".join(filter(None, [
            g["lot"], g["origin"] or "", g["process"] or "",
            " ".join(g["tasting_notes"]), "green unroasted"
        ]))
        parts.append(
            f"<article class='card' data-sec='green' data-idx='{idx}'"
            f" data-name=\"{esc(g['lot'])}\" data-roaster=\"{esc(g['roaster'])}\""
            f" data-origin=\"{esc(g['origin'] or 'Blend')}\""
            f" data-price='{price_attr}' data-score='{score_val}'"
            f" data-new='0'"
            f" data-search=\"{esc(search_text)}\">"
            f"<h2>{esc(g['lot'])} <span class='badge green'>GREEN</span></h2>"
            f"<p class='roaster'>{esc(g['roaster'])} &middot; {esc(g['origin'] or 'Blend')}{arrival}</p>"
            f"<p class='proc'>{esc(g['process'] or '')}</p>"
            f"<p class='notes'>{notes}</p>"
            f"<p>Cupping score: {score}</p>"
            f"<p class='price'>{price}</p>"
            f"<a href='{esc(g['url'])}' target='_blank'>View lot &rarr;</a>"
            f"</article>"
        )
    parts.append("</div></section>")

parts.append(
    "<footer>Data updated " + data["meta"]["updated_at"][:10]
    + " &middot; " + str(len(beans)) + " roasted beans from "
    + str(len({b["roaster"] for b in beans})) + " roaster(s)"
    + (f" &middot; {len(green)} green lots" if green else "")
    + " &middot; price sorting uses approximate USD conversion"
    + " &middot; curated by <a href='https://github.com/Ragingbaby23'>Ragingbaby23</a></footer>"
    + "<script>" + JS + "</script></body></html>"
)

out = ROOT / "site" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text("".join(parts), encoding="utf-8")
print("OK ->", out, out.stat().st_size, "bytes,", len(beans), "roasted +", len(green), "green")
