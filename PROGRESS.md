# Progress Log - Mind the Terroir

## Session 7 - 2026-11-16 — v2.1: ECOFARM 意可坊 (sumber green #3, dari China)
- Riset (research/ghands.md + sesi ini): GHands = trader WeChat-only, katalog tak bisa diambil dari luar China (Sogou captcha, XHS blok IP, Douyin search login-wall). Ecofarm 意可坊 = Nanjing Eco Farm Trading Co. (founder Catherine Gu/顾沁如, buyer BOP) — PUNYA toko Taobao publik tanpa login: taobao.com/list/dianpu/415487444.
- DONE (v2.1): scripts/fetch_ecofarm.py — 56 lot green Ecofarm (Panama 15, Ethiopia 14, Kenya 6, Colombia 4, CR 3, Honduras 3, Brazil 2, Nicaragua 1, China 1, 7 blend espresso). Harga CNY per pack (berat pack tak terlihat — halaman produk & halaman 2 toko = login wall) -> field baru price_display "¥X / pack", price_per_lb=null (jujur, jangan nebak berat). Origin/process/varietas diparse dari judul Mandarin (CN_ORIGIN/CN_VARIETY/CN_PROCESS, cek panjang-dulu).
- DATA MODEL: green lot kini boleh bawa price_display (teks harga apa adanya); renderer green card pakai price_per_lb -> "$X/lb", else price_display -> teks, else "Contact seller". data-price sort attr tetap hanya per-lb (Ecofarm sort harga = nempel di ujung; per-pack vs per-lb memang nggak comparable).
- INTEGRASI CRON: update_all.sh kini panggil fetch_ecofarm.py sebelum green_beans.py; green_beans.py merge data/ecofarm_beans.json kalau ada (fetch gagal -> lanjut data lama). Wrapper /root/.hermes/scripts/mtt-update-all.sh SUDAH di-cp ulang (aturan: salinan, bukan symlink).
- BUG: regex href Taobao paksa `\.htm"` padahal href bawa `?spm=...` -> 0 hasil dengan halaman sehat. Fix: `[^"]+` + split('?'). LESSON: kalau regex 0 hasil tapi retry-check item-title lolos, bedakan "halaman shell" vs "regex salah" — print count struktur dulu.
- Taobao quirk: fetch polos kadang balas shell SPA kosong (transient) -> fetch_with_retry 4x backoff, deteksi `item-title >= 5`.
- VERIFIKASI: local browser (total 630, green 410, filter roaster Ecofarm=56 kartu ¥, 0 contact-seller, name-sort OK) + live HTTP 200 (410 green, ¥105/¥96/¥100 kebaca).
- STATUS SITE: 630 kartu = 220 roasted + 410 green (Shrub 222 + C2C 132 + Ecofarm 56).

## Session 6 - 2026-11-15 — v2.0: SECTION TERPISAH + FILTER/SORT
- DONE (v2.0): situs kini DUA SECTION terpisah penuh — "Roasted Beans" (220) dan "Green Beans" (354), masing-masing header besar + counter live + divider; section kosong auto-sembunyi pas difilter.
- DONE (v2.0): filter/sort client-side — dropdown Section (all/roasted/green), Roaster, Origin (gabungan kedua dataset), Sort (Featured / Name A–Z / Price ↑↓ / Cupping score ↓ / Newest). Filter = AND; search tetap jalan bareng filter.
- KEPUTUSAN: sort harga roasted campur mata uang (USD/EUR/AED) -> pakai konversi KIRA-KIRA ke USD (RATE_TO_USD di generate.py) CUMA buat urutan; harga tampil tetap mata uang asli; footer diberi disclaimer. Lot "Contact seller" (data-price kosong) selalu di ujung sort harga (Infinity).
- CARA KERJA SORT: tiap kartu bawa data-attrs (data-sec/idx/name/roaster/origin/price/score/new/search); JS sort lalu re-append ke grid masing-masing section (appendChild = reorder DOM).
- BUG FIX: data-search & semua atribut kartu kini di-escape (html.escape) — nama bean/notes dengan apostrof sebelumnya bisa merusak HTML. NOTES: escape per item SEBELUM join pakai &bull; (escape hasil join = double-escape, entity jadi tampil literal — ketahuan pas review sendiri).
- VERIFIKASI: browser test full (default 574, green-only 354 & section roasted hilang, Archers 197, Ethiopia 44+73, price-up min $5.72 duluan, score-down 94.0 duluan, newest 6 NEW duluan, search 'Crop to Cup' 128). False alarm sekali: filter Ethiopia "0 green" ternyata filter roaster Archers masih nyangkut (AND behavior BENAR) — tes salah, bukan kode. Live: HTTP 200, kedua section + sort terkonfirmasi di curl.
- COSMETIC: dropdown dikasih label jelas ("Section: all", "Roaster: all", dst) — sebelumnya tiga "All" polos ambigu.
- Cron harian tak tersentuh (generate.py dipanggil update_all.sh, wrapper .hermes/scripts/ tidak berubah).

## Session 5 - 2026-11-12 — CRON HARIAN (v1.0 SELESAI)
- DONE (v1.0): cron harian `mind-the-terroir daily update` (job 7adae107f6bc) — jam 02:30 WIB (Asia/Jakarta), mode no_agent (script murni, tanpa LLM), deliver ringkasan 2 baris ke chat Telegram; gagal -> alert + cuplikan log.
- DONE: pipeline scripts/update_all.sh teruji full-auto 3x (exit 0): fetch roasted+green -> guard rails (roasted<20/green<100=ABORT tanpa deploy) -> render -> commit main -> deploy gh-pages -> verifikasi live. Rotasi lineup terlihat nyata: 218 -> 219 -> 221 roasted.
- BUG FIX: cron wrapper mtt-update-all.sh di /root/.hermes/scripts/ (cron cuma terima path relatif folder itu, symlink ditolak "traversal") — stdout pipeline harus di-null karena say() pakai tee ke log yang sama -> baris dobel. Wrapper = SALINAN: kalau update_all.sh diubah, cp ulang ke .hermes/scripts/.
- STATUS v1.0 PRD: SEMUA 4 DEFINISI SELESAI (site live + 5 roaster & 350 green + full-auto teruji + koreksi <5menit teruji sesi 3).
- NEXT (v2 opsional): Red Fox (PDF, dilewatkan curator), filter/sort, riwayat harga, notif beans baru, foto lot green.

## Session 4 (lanjutan sore) - 2026-11-10 — SECTION GREEN BEANS
- DONE (v0.4): section GREEN BEANS live — 350 lot: Coffee Shrub 222 (katalog sweetmarias.com, parse kartu HTML koleksi: score/arrival/process/notes/harga) + Crop to Cup 128 (WooCommerce /shop/ 8 halaman pertama; harga = max range varian, lot $0-only -> "Contact seller for price"). Kartu: GREEN badge, origin (heuristik nama lot, 58 None = blend wajar), process, notes (Shrub saja), cupping score (Shrub saja), $/lb, link lot. Footer + search client-side gabungan (try: search "Crop to Cup" -> 128).
- BUG adapter: regex anchor href+title di Sweet Maria's match DUA link per kartu (judul + tombol "View Details") -> 12 lot sampah "View Details" + setengah data hilang (21/page vs 40 kartu). Fix: buang anchor title="View Details" sebelum segmentasi. Total jadi 350 lot bersih, semua ada harga.
- DECISION: Red Fox Coffee Merchants (offer list = PDF mingguan, harga lengkap $/lb) DITUNDA ke sesi berikut — parse PDF beda adapter.
- CATATAN: Coffee Shrub = Shopify tapi score/arrival cuma ada di kartu HTML koleksi, BUKAN di products.json — makanya parse HTML bukan JSON.
- SITE SEKARANG: live 568 kartu (218 roasted: Prodigal 12, Sey 8, Tanat 2, Aviary 1, Archers 195 + 350 green).
- NEXT (v1.0): adapter Red Fox (PDF) + cron harian full-auto (fetch roasted + green -> render -> deploy)

## Session 4 - 2026-11-10 (kolisi sesi paralel + rekonsiliasi)
- DONE (v0.3): adapter Sey (8) + Archers (195) -> beans.json 218 beans (Prodigal 12, Tanat 2, Aviary 1). Semua roaster kini terisi.
- INSIDEN: dua sesi Hermes jalan paralel di repo yang sama (chat lain). Sesi lain commit fetch_sey.py+fetch_archers.py (220 beans) + renderer currency symbol + deploy (30467e5/d84a999); dia anggap fetch_roasters.py punya aku "draft lama" dan hapus (3533b58). Deploy-ku gagal karena dia pindah HEAD ke gh-pages pas aku cp. LESSON: SATU sesi saja per repo — atau selalu `git fetch` + cek remote baru push. Adapter akhir: fetch_roasters.py tunggal (restore), fetch_sey/fetch_archers dihapus (parse mereka lebih kotor: origin bundle salah, notes Elpidio kosong, filler "a sweet/balanced profile").
- KEEP dari sesi lain: currency symbol per roaster di site/generate.py (USD $, EUR, AED) — bagus, dipakai render ini.
- KEPUTUSAN KURATOR (chat): Archers ambil SEMUA in-stock (195, non-kapsul/subscription/drip/box) — bukan cuma published-2026 (100).
- DATA: Sey via products.json (8, notes dari "In the cup we find..."; origin dari suffix judul); Archers via products.json paginasi 2 hal, filter product_type "Roasted Coffee" + exclude capsule/subscription/drip/box + in-stock (195; 100 published 2026; 8 is_new <=30 hari). Origin Archers: prefix judul sebelum " - " divalidasi vs daftar negara; kapsul/dll tak masuk. img langsung dari products.json (images[0].src) — nggak perlu fetch per-produk.
- VERIFIKASI: URL produk Tanat (2) & Aviary (1) masih HTTP 200 (2026-11-10).
- NEXT (v0.3 terakhir): cron harian (updater full-auto) -> PRD v1.0

## Session 3 - 2026-11-10
- DONE (v0.3): foto produk di tiap kartu — scripts/fetch_images.py (15/15 dapat: Prodigal via {url}.json Shopify, Aviary+Tanat via og:image; http:// dipaksa https://). Renderer: <img class='pic'> square crop + loading='lazy'. Deploy live, verifikasi screenshot OK.
- FIX DATA: slug "taste-of-prodigal-sampler" 404 -> sebenarnya "taste-of-prodigal-samplers" (ketahuan pas fetch gambar). LESSON: fetch gambar = bonus verifikasi URL produk.
- CATATAN: gambar hotlink dari CDN roaster (Shopify/WordPress) — nggak disimpan lokal. Kalau roaster hapus produk, slot jadi kosong tapi kartu tetap tampil (img gagal silent).
- NEXT (v0.3 lanjutan): adapter Sey & Archers + verifikasi Tanat/Aviary + cron harian

## Session 2 - 2026-11-10
- DONE (v0.3): gh auth device flow (login Ragingbaby23) + repo github.com/Ragingbaby23/mind-the-terroir (public, semua commit ter-push)
- DONE (v0.3): GitHub Pages aktif -> https://ragingbaby23.github.io/mind-the-terroir/ (build_type legacy, branch gh-pages / root, HTTPS enforced). Verifikasi: HTTP 200 + <title> kebaca.
- LESSON: situs ada di site/ -> deploy pakai branch orphan gh-pages (isi: index.html hasil render doang); main tetap bersih. Workflow: checkout --orphan gh-pages -> rm --cached -> cp site/* ke root -> commit -> push -> balik main (checkout -f kalau untracked conflict).
- INFO: beans.json per 2026-11-10 = 15 beans (Prodigal 12, Tanat 2, Aviary 1; Sey & Archers masih 0) — adapter #2-5 belum lengkap walau roasters sudah dideklarasi. Memory lama sempat basi (bilang 12 beans/v0.1) karena sesi adapter nggak sempat dicatat di PROGRESS.md -> selalu update log di akhir sesi.
- NEXT (v0.3 lanjutan): adapter Sey & Archers (butuh data) + verifikasi/mateni adapter Tanat (2) & Aviary (1, cek lazy-load) + cron harian

## Session 1 - 2026-11-06
- DONE: PRD final (nama: Mind the Terroir; situs English; hosting GitHub Pages; curator punya akun GitHub)
- DONE: Roster final (konfirmasi curator): Prodigal (Boulder CO) / Sey (Brooklyn NY) / Aviary (US) / Tanat (Paris) / Archers (Sharjah UAE, archerscoffee.com)
- DONE: Adapter #1 Prodigal-US -> 12 beans asli di data/beans.json (nama, notes, proses, origin, harga USD, 1/12 url diverifikasi langsung (gesha-harmony); sisanya pola slug Shopify, url_verified=false)
- LESSON: prodigalroasters.com (SG) != getprodigal.com (US). Selalu verifikasi identitas+lokasi roaster sebelum fetch.
- LESSON: kalau parser dapat 0 hasil, PRINT DATA MENTAH DULU — struktur extraction bisa beda antar-fetch (2 varian di Prodigal). Parser sekarang handle keduanya.
- INFO: every.coffee = fallback terverifikasi untuk kelima roaster (ada harga)
- DONE (v0.2): renderer site/generate.py -> site/index.html (kartu beans + search client-side)
- NEXT (v0.3): adapter Sey/Aviary/Tanat/Archers + gh auth (device flow, password TIDAK PERNAH lewat chat) + repo GitHub Ragingbaby23 + deploy GitHub Pages
- RESOLVED: username GitHub = Ragingbaby23 (email git lokal sudah benar)
- OPEN: konfirmasi mata uang per roaster saat adapter aktif | cross-check jumlah produk vs every.coffee | cek lazy-load/pagination
