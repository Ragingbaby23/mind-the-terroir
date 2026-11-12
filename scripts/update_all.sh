#!/bin/bash
# update_all.sh - pipeline harian Mind the Terroir (v1.0)
# Alur: fetch roasted (Sey+Archers) -> isi foto yang kurang -> fetch green
#       -> render -> guard rails -> commit main -> deploy gh-pages -> verifikasi
# Guard: kalau data aneh (terlalu sedikit / 0), ABORT tanpa deploy.
# Kalau fetch satu sumber gagal, lanjut sumber lain (partial update lebih baik
# dari nggak update), TAPI total hasil nyaris 0 = jangan deploy.

set -u
cd /root/projects/mind-the-terroir
LOG=/tmp/mtt_update.log
stamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
say() { echo "[$(stamp)] $*" | tee -a "$LOG"; }

say "=== mulai update harian ==="

# ---------- 1. FETCH ----------
say "fetch roasted (Sey + Archers, replace)..."
python3 scripts/fetch_roasters.py >>"$LOG" 2>&1 || say "PERINGATAN: fetch_roasters gagal (lanjut dengan data lama)"

say "isi foto produk yang kurang..."
python3 scripts/fetch_images.py >>"$LOG" 2>&1 || say "PERINGATAN: fetch_images gagal (lanjut)"

say "fetch green beans (Coffee Shrub + Crop to Cup, replace)..."
python3 scripts/green_beans.py >>"$LOG" 2>&1 || say "PERINGATAN: green_beans gagal (lanjut dengan data lama)"

# ---------- 2. GUARD RAILS ----------
ROASTED=$(python3 -c "import json;print(len(json.load(open('data/beans.json'))['beans']))")
GREEN=$(python3 -c "import json;print(len(json.load(open('data/green_beans.json'))['lots']))")
say "jumlah: roasted=$ROASTED green=$GREEN"

if [ "$ROASTED" -lt 20 ] || [ "$GREEN" -lt 100 ]; then
    say "ABORT: jumlah tidak wajar (biasanya roasted ~218, green ~350). Kemungkinan sumber down / struktur berubah. TIDAK deploy; cek $LOG"
    exit 1
fi

# ---------- 3. RENDER ----------
say "render site..."
python3 site/generate.py >>"$LOG" 2>&1 || { say "ABORT: render gagal"; exit 1; }

# ---------- 4. COMMIT MAIN ----------
say "commit main..."
git add -A
git commit -q -m "daily auto-update: roasted $ROASTED + green $GREEN $(date -u +%F)" \
    || say "tidak ada perubahan (commit kosong OK)"
git push -q origin main || { say "ABORT: push main gagal"; exit 1; }

# ---------- 5. DEPLOY GH-PAGES ----------
say "deploy gh-pages..."
git branch -D gh-pages 2>/dev/null
git checkout -q --orphan gh-pages
git rm -r --cached . -q
cp site/index.html .
git add index.html
git commit -q -m "gh-pages: daily render $(date -u +%F)"
git push -q -f origin gh-pages
git checkout -q -f main
git branch -D gh-pages -q
rm -f index.html 2>/dev/null; rm -f generate.py 2>/dev/null

# ---------- 6. VERIFIKASI ----------
for i in $(seq 1 18); do
    s=$(gh api repos/Ragingbaby23/mind-the-terroir/pages --jq .status 2>/dev/null)
    [ "$s" = "built" ] && { say "Pages: BUILT (sekitar attempt $i)"; break; }
    [ "$i" -eq 18 ] && { say "PERINGATAN: Pages belum built setelah 3 menit (terakhir: $s)"; exit 2; }
    sleep 10
done
LIVE=$(curl -s https://ragingbaby23.github.io/mind-the-terroir/ | grep -o "badge green" | wc -l)
say "live check: $LIVE kartu green di situs (harusnya ~$GREEN)"
say "=== selesai ==="
