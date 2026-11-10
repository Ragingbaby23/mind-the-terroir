# fetch_images.py - isi field `image` tiap bean di beans.json
# Strategi per platform:
#   - Shopify (Prodigal, Aviary): GET {url_produk}.json -> images[0].src
#     (kalau .json gagal, fallback og:image dari HTML)
#   - WordPress/WooCommerce (Tanat): og:image dari HTML produk
# Prinsip PRD: kalau hasil 0 / error, PRINT DATA MENTAH DULU.

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEANS = ROOT / "data" / "beans.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; mind-the-terroir/0.3)"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def img_via_shopify_json(url):
    try:
        d = json.loads(fetch(url.rstrip("/") + ".json"))
        return d["product"]["images"][0]["src"]
    except Exception as e:
        print(f"  [json gagal] {e}")
        return None


def img_via_og(url):
    try:
        html = fetch(url)
        m = re.search(
            r'<meta property="og:image" content="([^"]+)"', html
        )
        return m.group(1) if m else None
    except Exception as e:
        print(f"  [og gagal] {e}")
        return None


data = json.loads(BEANS.read_text(encoding="utf-8"))
ok = fail = 0
for b in data["beans"]:
    if b.get("image"):
        print(f"[skip] {b['name']} (sudah ada)")
        continue
    print(f"[fetch] {b['roaster']}: {b['name']}")
    img = None
    if "getprodigal.com" in b["url"]:          # Shopify terverifikasi
        img = img_via_shopify_json(b["url"])
    if img is None:
        img = img_via_og(b["url"])             # fallback semua platform
    if img:
        # paksa https (aviary kadang kasih http://, mixed content di Pages)
        if img.startswith("http://"):
            img = "https://" + img[len("http://"):]
        b["image"] = img
        ok += 1
        print(f"  -> {img[:90]}")
    else:
        fail += 1
        print("  -> GAGAL, cek data mentah")

BEANS.write_text(
    json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(f"\nSelesai: {ok} dapat gambar, {fail} gagal, total beans {len(data['beans'])}")
