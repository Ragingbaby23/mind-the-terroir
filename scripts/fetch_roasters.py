# fetch_roasters.py - adapter Shopify untuk Sey & Archers -> data/beans.json
# Sumber: /collections/.../products.json (Shopify public JSON API)
#   Sey:     seycoffee.com/collections/coffee        (8 produk)
#   Archers: archerscoffee.com/collections/all        (paginasi, filter product_type)
# Merge: beans milik roaster ini di-replace total; roaster lain nggak disentuh.
# Prinsip PRD: hasil 0 -> PRINT DATA MENTAH DULU.

import json
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEANS = ROOT / "data" / "beans.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; mind-the-terroir/0.3)"}
TODAY = date.today().isoformat()

SHOP_ROASTERS = {
    "Sey": {
        "pages": ["https://www.seycoffee.com/collections/coffee/products.json?limit=250"],
        "currency": "USD",
        "product_type": None,          # semua produk di koleksi ini memang coffee
        "exclude_title": None,
    },
    "Archers": {
        "pages": [
            f"https://archerscoffee.com/collections/all/products.json?limit=250&page={p}"
            for p in (1, 2)
        ],
        "currency": "AED",
        "product_type": "Roasted Coffee",  # buang alat/buku/cups
        # buang kapsul, subscription, drip bag, box set
        "exclude_title": re.compile(r"capsule|subscription|drip|box of", re.I),
    },
}

NOTE_RE = re.compile(
    r"in the cup we find ([a-z][^.]*?)\.", re.I
)
KNOWN_PROCESS = re.compile(
    r"\b(washed|natural|honey|anaerobic|decaf|decaffeinated)\b", re.I
)


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def min_price(p):
    """Harga varian termurah + flag from (ada >1 varian/ukuran)."""
    prices = [float(v["price"]) for v in p["variants"] if v.get("price")]
    if not prices:
        return None, False
    return min(prices), len(prices) > 1


def in_stock(p):
    return any(v.get("available") for v in p.get("variants", []))


def split_origin_title(title):
    """'Colombia - Finca X' -> ('Colombia', 'Finca X').
    Sey: '2026 Chelbessa; 2nd Selection - Ethiopia' -> ('Ethiopia', '2026 Chelbessa; 2nd Selection')."""
    if " - " in title:
        head, tail = title.split(" - ", 1)
        if head.isupper() or len(head.split()) <= 2:
            return head.strip(), tail.strip()          # Archers: origin di depan
        return tail.strip(), head.strip()              # Sey: origin di belakang
    return None, title


def parse_notes(body_html):
    text = re.sub(r"<[^>]+>", " ", body_html or "")
    text = re.sub(r"\s+", " ", text)
    m = NOTE_RE.search(text)
    if not m:
        return []
    raw = m.group(1).strip().rstrip(".")
    raw = raw.replace(", and ", ", ").replace(" and ", ", ")
    parts = [s.strip().lower() for s in raw.split(",") if s.strip()]
    return [p for p in parts if len(p) > 2]


def parse_process(title, body_html):
    text = (title or "") + " " + re.sub(r"<[^>]+>", " ", body_html or "")
    m = KNOWN_PROCESS.search(text)
    return m.group(1).title() if m else ""


def shopify_bean(roaster, p, currency):
    origin, name = split_origin_title(p["title"])
    price, from_flag = min_price(p)
    img = (p.get("images") or [{}])[0].get("src")
    if img and img.startswith("http://"):   # paksa https (mixed content)
        img = "https://" + img[len("http://"):]
    published = (p.get("published_at") or "")[:10]
    is_new = bool(published) and (
        date.fromisoformat(TODAY) - date.fromisoformat(published)
    ).days <= 30
    return {
        "id": f"{roaster.lower()}-{p['handle']}",
        "roaster": roaster,
        "name": name,
        "origin": origin or "",
        "process_variety": parse_process(p["title"], p.get("body_html")),
        "tasting_notes": parse_notes(p.get("body_html")),
        "price": {
            "amount": price,
            "currency": currency,
            "from": from_flag,
        },
        "availability": "available" if in_stock(p) else "sold_out",
        "is_new": is_new,
        "url": f"https://{'www.seycoffee.com' if roaster == 'Sey' else 'archerscoffee.com'}/products/{p['handle']}",
        "url_verified": True,
        "last_updated": TODAY,
        "image": img or "",
    }


def main():
    data = json.loads(BEANS.read_text(encoding="utf-8"))
    new_beans = []
    for roaster, cfg in SHOP_ROASTERS.items():
        prods = []
        for url in cfg["pages"]:
            d = fetch(url)
            got = d.get("products", [])
            if not got:
                print(f"[{roaster}] 0 produk dari {url} — DATA MENTAH: {str(d)[:400]}")
            prods += got
        if cfg["product_type"]:
            prods = [p for p in prods if p.get("product_type") == cfg["product_type"]]
        if cfg["exclude_title"]:
            prods = [p for p in prods if not cfg["exclude_title"].search(p["title"])]
        prods = [p for p in prods if in_stock(p)]
        beans = [shopify_bean(roaster, p, cfg["currency"]) for p in prods]
        print(f"[{roaster}] {len(beans)} beans in-stock")
        new_beans += beans

    if not new_beans:
        print("TOTAL 0 — jangan tulis beans.json, cek data mentah dulu")
        return

    keep = [b for b in data["beans"] if b["roaster"] not in SHOP_ROASTERS]
    data["beans"] = keep + new_beans
    data["meta"]["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    from collections import Counter
    data["meta"]["note"] = "beans per roaster: " + ", ".join(
        f"{r} {c}" for r, c in sorted(Counter(b["roaster"] for b in data["beans"]).items())
    )
    BEANS.write_text(
        json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"beans.json total: {len(data['beans'])}")


if __name__ == "__main__":
    main()
