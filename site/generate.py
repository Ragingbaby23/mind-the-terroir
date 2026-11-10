# generate.py - Mind the Terroir (v0.2)
# Baca data/beans.json -> tulis site/index.html
# Cuma pakai konsep level kita: dict, list, for, f-string.

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # naik 1 folder = folder project
data = json.loads((ROOT / "data" / "beans.json").read_text(encoding="utf-8"))
beans = data["beans"]

CSS = """
:root { --bg:#171310; --card:#211b16; --line:#3a2f26; --ink:#efe7dc; --mut:#a89a8a; --acc:#d9a05b; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; }
header { padding:40px 20px 12px; text-align:center; }
h1 { margin:0; font-size:2rem; letter-spacing:.5px; }
h1 span { color:var(--acc); }
.tag { color:var(--mut); margin:6px 0 18px; }
#q { width:min(520px,90%); padding:10px 14px; border-radius:10px; border:1px solid var(--line); background:var(--card); color:var(--ink); font-size:1rem; }
.meta { color:var(--mut); font-size:.85rem; margin:10px 0 0; }
main { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; padding:24px; max-width:1100px; margin:0 auto; }
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
footer { text-align:center; color:var(--mut); padding:24px; font-size:.85rem; border-top:1px solid var(--line); }
footer a { color:var(--mut); text-decoration:underline; }
"""

JS = """
const q = document.getElementById('q');
const cards = [...document.querySelectorAll('.card')];
const countEl = document.getElementById('count');
function update(){
  const s = q.value.toLowerCase();
  let n = 0;
  cards.forEach(c => {
    const hit = (c.dataset.search + ' ' + c.textContent).toLowerCase().includes(s);
    c.style.display = hit ? '' : 'none';
    if (hit) n++;
  });
  countEl.textContent = n + ' of ' + cards.length + ' beans';
}
q.addEventListener('input', update);
update();
"""

def price_text(p):                                   # dict di dalam dict: p["amount"]
    t = f"${p['amount']:.2f} {p['currency']}"
    return f"from {t}" if p["from"] else t

parts = []
parts.append(
    "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    "<title>Mind the Terroir</title><style>" + CSS + "</style></head><body>"
    "<header><h1>Mind the <span>Terroir</span></h1>"
    "<p class='tag'>Fresh beans, five roasters, one place.</p>"
    "<input id='q' placeholder='Search beans, origins, notes...' autocomplete='off'>"
    "<p class='meta' id='count'></p></header><main>"
)

for b in beans:                                      # <- loop inti project ini
    notes = " &bull; ".join(b["tasting_notes"]) if b["tasting_notes"] else "&mdash;"
    badges = ""
    if b["is_new"]:
        badges += "<span class='badge new'>NEW</span>"
    if b["availability"] == "sold_out":
        badges += "<span class='badge out'>SOLD OUT</span>"
    search_text = b["name"] + " " + (b["origin"] or "") + " " + " ".join(b["tasting_notes"])
    img = (
        f"<img class='pic' src='{b['image']}' alt='' loading='lazy'>"
        if b.get("image") else ""
    )
    parts.append(
        f"<article class='card' data-search='{search_text}'>"
        f"{img}"
        f"<h2>{b['name']} {badges}</h2>"
        f"<p class='roaster'>{b['roaster']} &middot; {b['origin'] or 'Blend'}</p>"
        f"<p class='proc'>{b['process_variety'] or ''}</p>"
        f"<p class='notes'>{notes}</p>"
        f"<p class='price'>{price_text(b['price'])}</p>"
        f"<a href='{b['url']}' target='_blank'>View at roaster &rarr;</a>"
        f"</article>"
    )

parts.append(
    "</main><footer>Data updated " + data["meta"]["updated_at"][:10]
    + " &middot; " + str(len(beans)) + " beans from "
    + str(len({b["roaster"] for b in beans})) + " roaster(s)"
    + " &middot; curated by <a href='https://github.com/Ragingbaby23'>Ragingbaby23</a></footer>"
    + "<script>" + JS + "</script></body></html>"
)

out = ROOT / "site" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text("".join(parts), encoding="utf-8")
print("OK ->", out, out.stat().st_size, "bytes,", len(beans), "beans")
