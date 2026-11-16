# fetch_ecofarm.py - adapter green coffee: Ecofarm 意可坊 (Nanjing Eco Farm Trading, China)
# Sumber: toko Taobao "意可坊咖啡" — https://www.taobao.com/list/dianpu/415487444.htm
# Halaman list toko kebuka TANPA login (halaman detail produk & halaman 2 = login wall),
# jadi ambil judul + harga + URL dari kartu list aja.
# Harga Taobao = per pack (berat pack nggak terlihat dari list) -> simpan apa adanya
# sebagai price_display "¥X / pack"; price_per_lb = None (jujur, jangan nebak berat).
# Output: data/ecofarm_beans.json

import html
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "ecofarm_beans.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept-Language": "zh-CN,zh;q=0.9"}
STORE = "https://www.taobao.com/list/dianpu/415487444.htm"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def fetch_with_retry(url, tries=4):
    # Taobao kadang balas shell SPA kosong (bot-wall transient) -> retry + backoff
    last = ""
    for i in range(tries):
        last = fetch(url)
        if last.count("item-title") >= 5:
            return last
        print(f"  [attempt {i+1}: halaman shell tanpa item, retry...]")
        time.sleep(3 + i * 2)
    return last


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ---------- origin: kata kunci Mandarin di judul ----------
CN_ORIGIN = [
    ("Ethiopia", ["埃塞", "瑰夏村", "耶加雪菲", "西达摩", "古伎"]),
    ("Panama", ["巴拿马"]),
    ("Colombia", ["哥伦比亚"]),
    ("Kenya", ["肯尼亚"]),
    ("Brazil", ["巴西"]),
    ("Honduras", ["洪都拉斯"]),
    ("Costa Rica", ["哥斯达黎加"]),
    ("Nicaragua", ["尼加拉瓜"]),
    ("Uganda", ["乌干达"]),
    ("Peru", ["秘鲁"]),
    ("China", ["中国", "云南"]),
    ("Guatemala", ["危地马拉"]),
    ("Mexico", ["墨西哥"]),
    ("El Salvador", ["萨尔瓦多"]),
    ("Rwanda", ["卢旺达"]),
    ("Indonesia", ["印尼", "印度尼西亚"]),
    ("Papua New Guinea", ["巴布亚"]),
]

# ---------- varietas: cek urutan panjang-dulu ----------
CN_VARIETY = [
    ("Geisha 1931", ["瑰夏1931"]),
    ("Geisha", ["瑰夏"]),
    ("74158", ["74158"]),
    ("74112", ["74112"]),
    ("74110", ["74110"]),
    ("SL28", ["sl28"]),
    ("SL34", ["sl34"]),
    ("SL14", ["sl14"]),
    ("Ruiru 11", ["鲁伊鲁 11", "鲁伊鲁11"]),
    ("Batian", ["巴蒂安"]),
    ("Yellow Bourbon", ["黄波旁"]),
    ("Bourbon", ["波旁"]),
    ("Typica", ["铁皮卡"]),
    ("Catuai", ["卡杜艾"]),
    ("Caturra", ["卡杜拉"]),
    ("Catimor", ["卡蒂姆"]),
    ("Heirloom", ["原生种"]),
    ("Lempira", ["伦皮拉"]),
    ("Ihcafe 90", ["ihcafe 90", "ihcafe90"]),
    ("Nyassaland", ["尼亚萨兰"]),
    ("Acaia & IAC-125RN", ["阿卡伊&iac-125rn", "阿卡伊 &iac-125rn"]),
]

# ---------- proses: cek urutan panjang-dulu ----------
CN_PROCESS = [
    ("Temp-controlled anaerobic natural", ["控温厌氧发酵日晒"]),
    ("Double-ferment washed", ["双重发酵水洗"]),
    ("Anaerobic natural (MOSTO)", ["厌氧日晒mosto", "厌氧日晒 mosto"]),
    ("Anaerobic natural", ["厌氧日晒"]),
    ("Anaerobic washed", ["厌氧水洗"]),
    ("Anaerobic honey", ["厌氧蜜"]),
    ("Red honey", ["红蜜"]),
    ("Black honey", ["黑蜜"]),
    ("Honey", ["蜜处理"]),
    ("Hybrid washed", ["混合水洗"]),
    ("Pulped natural", ["半日晒"]),
    ("Washed", ["水洗"]),
    ("Natural", ["日晒"]),
]


def find_first(title, table):
    t = title.lower()
    for value, keys in table:
        for k in keys:
            if k in t:
                return value
    return None


def clean_lot_name(title):
    # buang suffix toko, jaga tahun + 空运/海运 (info logistik!)
    name = clean(html.unescape(title))
    for junk in ["意可坊意式拼配咖啡生豆", "意可坊咖啡生豆", "咖啡生豆"]:
        name = name.replace(junk, "")
    name = clean(name.replace("意可坊", ""))
    name = re.sub(r"(\s*生豆)+\s*$", "", name)   # sisa suffix " 生豆"
    return clean(name)


def parse_ecofarm():
    lots = []
    for page, url in [(1, STORE), (2, STORE.replace(".htm", "_2.htm"))]:
        try:
            h = fetch_with_retry(url)
        except Exception as e:
            print(f"  [page {page} gagal: {e}]")
            break
        # kartu: <a href=".../list/item/XXX.htm?spm=..." class="item"> ... item-title ... disc-price
        # (href bawa query spm -> jangan paksa .htm" di ujung)
        blocks = re.findall(
            r'<a href="(https://www\.taobao\.com/list/item/[^"]+)"[^>]*class="item"[^>]*>'
            r'.*?item-title">([^<]+)<.*?disc-price">([^<]+)<', h, re.S)
        n0 = len(lots)
        for url_i, title, price in blocks:
            title = clean(title)
            if "生豆" not in title:        # cuma green beans (skip gadget 滤纸/cangkir dll)
                continue
            if "邮费" in title:            # link top-up ongkir, bukan produk
                continue
            try:
                price_cny = float(clean(price))
            except ValueError:
                continue
            variety = find_first(title, CN_VARIETY)
            process = find_first(title, CN_PROCESS)
            proc_field = " · ".join(x for x in (variety, process) if x) or None
            lots.append({
                "lot": clean_lot_name(title),
                "roaster": "Ecofarm 意可坊",
                "origin": find_first(title, CN_ORIGIN),   # 拼配 tanpa negara -> None
                "process": proc_field,
                "tasting_notes": [],                      # judul Taobao nggak bawa notes
                "score": None,
                "arrival": None,
                "price_per_lb": None,                     # per pack, bukan per lb
                "price_display": f"¥{price_cny:g} / pack",
                "price_cny": price_cny,
                "currency": "CNY",
                "url": url_i.split("?")[0],
                "url_verified": False,
            })
        print(f"  page {page}: +{len(lots)-n0} lot (kartu terlihat: {len(blocks)})")
        if not blocks:
            break
        time.sleep(1)
    return lots


if __name__ == "__main__":
    print("== Ecofarm 意可坊 (Taobao 意可坊咖啡)")
    lots = parse_ecofarm()
    if not lots:
        print("  0 LOT! PRINT DATA MENTAH (aturan PRD):")
        try:
            print(fetch(STORE)[:3000])
        except Exception as e:
            print("  fetch ulang gagal:", e)
        raise SystemExit(1)

    data = {
        "meta": {
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "seller": "Nanjing Eco Farm Trading Co., Ltd. (南京意可坊进出口贸易有限公司)",
            "note": "Green beans per pack (bukan per lb) — harga Taobao apa adanya, CNY",
            "sources": ["taobao.com 意可坊咖啡 (dianpu 415487444)"],
        },
        "lots": lots,
    }
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nTotal: {len(lots)} lot")
    print("Contoh 3 pertama + 1 terakhir:")
    for l in lots[:3] + lots[-1:]:
        print(" ", json.dumps(l, ensure_ascii=False)[:170])
