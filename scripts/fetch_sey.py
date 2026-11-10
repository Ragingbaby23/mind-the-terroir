# fetch_sey.py - adapter #2 Sey (seycoffee.com, Brooklyn NY, USD)
# Sumber: Shopify collection /collections/coffee/products.json (terverifikasi
# 2026-11-10: 8 produk live; angka 61 di collections.json termasuk unpublished).
# Prinsip PRD: kalau hasil 0, PRINT DATA MENTAH DULU.

import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEANS = ROOT / "data" / "beans.json"
BASE = "https://www.seycoffee.com"
SRC = BASE + "/collections/coffee/products.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; mind-the-terroir/0.3)"}
ROASTER = "Sey"
CURRENCY = "USD"
TODAY = datetime.now(timezone.utc).date()


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def strip_tags(s):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def parse_notes(body):
    # pola tetap Sey: "In the cup we find X, Y, and Z."
    m = re.search(r"we find ([^.]+)", body, re.I)
    if not m:
        return []
    raw = m.group(1).lower().rstrip(".")
    # deskripsi macam "a sweet and balanced profile of X, Y, Z" -> potong ke notes
    raw = re.sub(r"^.*?profile of ", "", raw) if "profile of" in raw else raw
    parts = re.split(r",| and ", raw)
    return [p.strip() for p in parts if p.strip()][:5]


def parse_bean(p):
    title = p["title"]
    # "2026 Chelbessa; 2nd Selection - Ethiopia" -> name + origin
    if " - " in title:
        name, origin = title.rsplit(" - ", 1)
    else:
        name, origin = title, ""
        if "Huila" in (title + " " + (p["body_html"] or "")):
            origin = "Colombia"  # deskripsi menyebut San Agustin, Huila
    # proses kalau tersirat di judul (contoh: "White Honey")
    kw = [k for k in ("Washed", "Natural", "Honey", "Decaffeinated")
          if k.lower() in name.lower()]
    variants = [v for v in p["variants"] if v.get("price")]
    prices = [float(v["price"]) for v in variants]
    avail = any(v.get("available") for v in variants)
    pub = datetime.strptime(p["published_at"][:10], "%Y-%m-%d").date()
    return {
        "id": "sey-" + p["handle"],
        "roaster": ROASTER,
        "name": name,
        "origin": origin,
        "process_variety": " ".join(kw),
        "tasting_notes": parse_notes(strip_tags(p["body_html"])),
        "price": {
            "amount": min(prices),           # 250g = varian termurah
            "currency": CURRENCY,
            "from": len(set(prices)) > 1,
        },
        "availability": "available" if avail else "sold_out",
        "is_new": (TODAY - pub).days <= 30,
        "url": BASE + "/products/" + p["handle"],
        "url_verified": True,                # langsung dari API Shopify
        "last_updated": TODAY.isoformat(),
        "image": (p["images"][0]["src"] if p.get("images") else None),
    }


data = fetch(SRC + "?limit=250")
if not data["products"]:
    print("[ERROR] 0 produk — DATA MENTAH:")
    print(json.dumps(data, indent=1)[:2000])
    raise SystemExit(1)

new_beans = [parse_bean(p) for p in data["products"]]

beans = json.loads(BEANS.read_text(encoding="utf-8"))
beans["beans"] = [b for b in beans["beans"] if b["roaster"] != ROASTER] + new_beans
beans["meta"]["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
beans["meta"]["note"] = "5 roaster aktif: Prodigal, Sey, Aviary, Tanat, Archers"
for r in beans["roasters"]:
    if r["name"] == ROASTER:
        r["adapter_status"] = "active"

BEANS.write_text(json.dumps(beans, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"OK: {len(new_beans)} beans {ROASTER} masuk, total {len(beans['beans'])}")
for b in new_beans:
    print(f"  - {b['name']} | {b['origin']} | {b['price']['amount']} {CURRENCY} | notes: {b['tasting_notes']}")
