# Progress Log - Mind the Terroir

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
