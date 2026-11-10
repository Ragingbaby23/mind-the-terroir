# Progress Log - Mind the Terroir

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
