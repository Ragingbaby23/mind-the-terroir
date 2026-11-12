# green_beans.py - adapter green coffee: Coffee Shrub (Sweet Maria's) + Crop to Cup
# Output: data/green_beans.json (struktur sama seperti beans.json, + field green)
#   - Cupping score, arrival, process, notes, harga per lb
# Prinsip PRD: kalau parse dapat 0 hasil, PRINT DATA MENTAH DULU.

import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "green_beans.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ---------- ORIGIN: heuristik dari nama lot ----------
ORIGIN_HINTS = [
    ("Kenya", ["kenya", " aa", " ab", "nyeri", "embu", "machakos", "kagumoini",
               "gondo", "ngariama", "aak "]),
    ("Ethiopia", ["ethiopia", "yirga", "guji", "sidamo", "harrar", "jimma",
                  "illubabor", "kochere", "gedeb", "chelbesa", "wush",
                  "keramo", "bombe", "murago", "kokose", "shantawane",
                  "abaya", "bento", "danche", "chiro", "loisaba", "togeru"]),
    ("Philippines", ["96b liberica", "excelsa", "liberica"]),
    ("Burundi", ["burundi", "kibira", "muyinga", "kayanza"]),
    ("Rwanda", ["rwanda"]),
    ("Uganda", ["uganda", "sipi"]),
    ("Tanzania", ["tanzania", "kivu", "nyambo"]),
    ("Congo", ["congo", "kivu"]),
    ("Brazil", ["brazil", "cerrado", "minas", "moji", "santos", "canastra"]),
    ("Colombia", ["colombia", "huila", "narino", "cauca", "inza", "tolima",
                  "medellin", "antioquia", "excelso"]),
    ("Mexico", ["mexico", "chiapas", "oaxaca", "pluma"]),
    ("Guatemala", ["guatemala", "antigua", "huehue", "chimaltenango"]),
    ("Honduras", ["honduras", "comsa", "marcala"]),
    ("El Salvador", ["el salvador", "salvador"]),
    ("Nicaragua", ["nicaragua", "segovia", "jinotega"]),
    ("Costa Rica", ["costa rica", "tarraz", "helsar", "zarcero"]),
    ("Panama", ["panama", "boquete"]),
    ("Ecuador", ["ecuador", "loja", "pichincha"]),
    ("Peru", ["peru", "cajamarca"]),
    ("Bolivia", ["bolivia"]),
    ("Indonesia", ["indonesia", "sumatra", "java", "sulawesi", "toraja",
                   "flores", "bali", "mandheling", "gayo", "lintong"]),
    ("Papua New Guinea", ["papua", "png", "sigri"]),
    ("Laos", ["laos", "paksong"]),
    ("India", ["india", "monsooned", "malabar", "karnataka"]),
    ("Vietnam", ["vietnam", "robusta"]),
    ("Yemen", ["yemen", "haraz"]),
    ("Hawaii", ["kona", "hawaii", "maui", "ka'u", "kauai"]),
]


def guess_origin(name):
    n = " " + name.lower() + " "
    for origin, hints in ORIGIN_HINTS:
        for h in hints:
            if h in n:
                return origin
    return None


# ---------- 1. COFFEE SHRUB (Sweet Maria's) ----------
# Halaman koleksi berisi kartu lengkap: notes, score, arrival, process, harga.
# Paginasi ?page=N sampai nggak ada kartu lagi.
def parse_coffee_shrub():
    lots = []
    for page in range(1, 15):
        url = ("https://www.sweetmarias.com/collections/"
               f"green-coffee-coffee-shrub?page={page}")
        try:
            h = fetch(url)
        except Exception as e:
            print(f"  [page {page} gagal] {e}")
            break
        h = re.sub(r"\s+", " ", h)

        # tiap kartu punya 2 link: judul produk + tombol "View Details".
        # Ambil HANYA link judul (title != "View Details"), segment = antar judul.
        anchors = [a for a in re.finditer(
            r'href="[^"]*/products/([^"]+)"[^>]*title="([^"]+)"', h)
            if a.group(2).strip().lower() != "view details"]
        if not anchors:
            break
        page_count = 0
        for i, a in enumerate(anchors):
            end = anchors[i + 1].start() if i + 1 < len(anchors) else len(h)
            seg = h[a.start():end]
            name = clean(a.group(2))
            m = re.search(r"Score:\s*</span>\s*([0-9.]+)", seg)
            score = float(m.group(1)) if m else None
            m = re.search(r"Arrival:\s*</span>\s*([A-Za-z]+ \d{4})", seg)
            arrival = m.group(1) if m else None
            m = re.search(r"Process:\s*</span>\s*([^<]+?)\s*</div>", seg)
            process = clean(m.group(1)) if m else None
            notes = [clean(x) for x in
                     re.findall(r'flavor-item">([^<]*)<', seg)][:4]
            m = re.search(r"\$([0-9]+\.[0-9]{2})", seg)
            if not m:
                continue                      # kartu tanpa harga -> skip
            price = float(m.group(1))
            if "archived" in seg.lower() and score is None:
                continue                      # arsip tanpa data -> skip
            lots.append({
                "lot": name,
                "roaster": "Coffee Shrub",     # sumber (bukan roaster: green!)
                "origin": guess_origin(name),
                "process": process,
                "tasting_notes": notes,
                "score": score,
                "arrival": arrival,
                "price_per_lb": price,
                "currency": "USD",
                "url": f"https://www.sweetmarias.com/products/{a.group(1)}",
                "url_verified": False,
            })
            page_count += 1
        print(f"  page {page}: +{page_count} lot")
        if page_count == 0:
            break
        time.sleep(1)
    return lots


# ---------- 2. CROP TO CUP (WooCommerce) ----------
# Listing /shop/?product-page=N: <li class="product ...> tiap lot.
# Harga: range varian "0.00 - $X" -> pakai $X (harga/lb spot tertinggi).
# Sesuai keputusan: halaman harga $0-only tetap masuk, dengan catatan.
def parse_crop_to_cup():
    lots = []
    for page in range(1, 9):                  # cap 8 halaman = lot terbaru
        url = f"https://www.croptocup.com/shop/?product-page={page}"
        try:
            h = fetch(url)
        except Exception as e:
            print(f"  [page {page} gagal] {e}")
            break
        blocks = re.findall(r'<li class="product[^>]*>.*?</li>', h, re.S)
        if not blocks:
            break
        n0 = len(lots)
        for b in blocks:
            m = re.search(r'woocommerce-loop-product__title">([^<]+)', b)
            name = clean(m.group(1)) if m else None
            m = re.search(r'href="(https://www\.croptocup\.com/product/[^"]+)"', b)
            if not name or not m:
                continue
            prices = [float(x) for x in
                      re.findall(r"([0-9]+\.[0-9]{2})</bdi>", b)]
            top = max(prices) if prices else 0.0
            price = top if top > 0 else None     # 0-only -> None = contact
            m = re.search(r'data-product_sku="([^"]*)"', b)
            sku = m.group(1) if m else None
            cat = re.search(r"product_cat-([a-z-]+)", b)
            process = cat.group(1).replace("-", " ").title() if cat else None
            lots.append({
                "lot": name,
                "roaster": "Crop to Cup",
                "origin": guess_origin(name),
                "process": process,
                "tasting_notes": [],
                "price_per_lb": price,            # None = lihat halaman lot
                "currency": "USD",
                "url": m2.group(1) if (m2 := re.search(r'href="(https://[^"]+)"', b)) else url,
                "sku": sku,
                "url_verified": False,
            })
        print(f"  page {page}: +{len(lots)-n0} lot")
        time.sleep(1)
    return lots


if __name__ == "__main__":
    print("== Coffee Shrub (Sweet Maria's)")
    shrub = parse_coffee_shrub()
    print("== Crop to Cup")
    c2c = parse_crop_to_cup()

    data = {
        "meta": {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "note": "Green beans: beans mentah per lb, untuk roaster",
            "sources": ["sweetmarias.com (Coffee Shrub)", "croptocup.com"],
        },
        "lots": shrub + c2c,
    }
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    with_price = sum(1 for l in data["lots"] if l["price_per_lb"])
    print(f"\nTotal: {len(data['lots'])} lot ({with_price} dengan harga publik)")
    print("Row terakhir tiap sumber:")
    for src in ("Coffee Shrub", "Crop to Cup"):
        last = [l for l in data["lots"] if l["roaster"] == src][-1]
        print(" ", json.dumps(last, ensure_ascii=False)[:160])
