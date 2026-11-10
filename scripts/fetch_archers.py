# fetch_archers.py - adapter #5 Archers (archerscoffee.com, Sharjah UAE, AED)
# Sumber: Shopify collection /collections/coffee ("Our Coffee Selection",
# product_type Roasted Coffee; 197 produk live per 2026-11-10).
# Catatan: body_html = data teknis (Producer/Farm/Variety/Process/Altitude),
# tasting notes nyaris nggak ada di listing -> tasting_notes kosong.
# Prinsip PRD: kalau hasil 0, PRINT DATA MENTAH DULU.

import json
import re
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEANS = ROOT / "data" / "beans.json"
BASE = "https://archerscoffee.com"
SRC = BASE + "/collections/coffee/products.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; mind-the-terroir/0.3)"}
ROASTER = "Archers"
CURRENCY = "AED"
TODAY = datetime.now(timezone.utc).date()


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def strip_tags(s):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def parse_fields(body_html):
    # body format: <strong>Variety</strong>: Geisha<br> ...
    out = {}
    for m in re.finditer(r"<strong>\s*([A-Za-z ]{2,15})\s*</strong>\s*:\s*([^<]+)", body_html or ""):
        out[m.group(1).strip().lower()] = unescape(m.group(2).strip())
    return out


def parse_bean(p):
    title = p["title"]
    f = parse_fields(p["body_html"])
    # "Brazil - Fazenda IP" -> origin dari segmen pertama
    if " - " in title:
        origin = title.split(" - ", 1)[0].strip()
    else:
        origin = f.get("location", "").split(",")[-1].strip() or "Blend"
    # format Prodigal: "Washed Gesha" = proses + varietas
    pv = " ".join(x for x in (f.get("process", ""), f.get("variety", "")) if x).strip()
    variants = [v for v in p["variants"] if v.get("price")]
    avail_vs = [v for v in variants if v.get("available")]
    use = avail_vs or variants
    prices = [float(v["price"]) for v in use]
    pub = datetime.strptime(p["published_at"][:10], "%Y-%m-%d").date()
    return {
        "id": "archers-" + p["handle"],
        "roaster": ROASTER,
        "name": title,
        "origin": origin,
        "process_variety": pv,
        "tasting_notes": [],               # listing Archers tanpa cupping notes
        "price": {
            "amount": min(prices),          # varian termurah (mis. 50g)
            "currency": CURRENCY,
            "from": len(set(prices)) > 1,
        },
        "availability": "available" if avail_vs else "sold_out",
        "is_new": (TODAY - pub).days <= 30,
        "url": BASE + "/products/" + p["handle"],
        "url_verified": True,              # langsung dari API Shopify
        "last_updated": TODAY.isoformat(),
        "image": (p["images"][0]["src"] if p.get("images") else None),
    }


# pagination: products.json max 250/halaman
products, page = [], 1
while True:
    d = fetch(f"{SRC}?limit=250&page={page}")
    batch = d.get("products", [])
    if not batch:
        if page == 1:
            print("[ERROR] 0 produk — DATA MENTAH:")
            print(json.dumps(d, indent=1)[:2000])
            raise SystemExit(1)
        break
    products += batch
    if len(batch) < 250:
        break
    page += 1

new_beans = [parse_bean(p) for p in products]

beans = json.loads(BEANS.read_text(encoding="utf-8"))
beans["beans"] = [b for b in beans["beans"] if b["roaster"] != ROASTER] + new_beans
beans["meta"]["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
beans["meta"]["note"] = "5 roaster aktif: Prodigal, Sey, Aviary, Tanat, Archers"
for r in beans["roasters"]:
    if r["name"] == ROASTER:
        r["adapter_status"] = "active"

BEANS.write_text(json.dumps(beans, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"OK: {len(new_beans)} beans {ROASTER} masuk, total {len(beans['beans'])}")
from collections import Counter
print("per-origin:", dict(Counter(b["origin"] for b in new_beans).most_common(10)))
print("sold_out:", sum(1 for b in new_beans if b["availability"] == "sold_out"))
print("is_new:", sum(1 for b in new_beans if b["is_new"]))
print("tanpa gambar:", sum(1 for b in new_beans if not b["image"]))
print("tanpa process_variety:", sum(1 for b in new_beans if not b["process_variety"]))
