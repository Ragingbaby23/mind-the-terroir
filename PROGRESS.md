# Progress Log - Mind the Terroir

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
