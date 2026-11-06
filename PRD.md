# PRD - Mind the Terroir
**Version 1.0 - 2026-11-06** | Owner: Ragingbaby23 (curator) | Pair: Hermes

## 1. Masalah
Beans di roaster specialty ganti cepat — tiap minggu ada drop baru. Buat ngikutin 5 roaster sekaligus, orang harus buka 5 website satu-satu. Nggak ada satu tempat buat lihat & bandingin semuanya.

## 2. User
- **Curator (Ragingbaby23)** — input daftar roaster, koreksi data salah
- **Publik** — coffee enthusiast yang mau lihat katalog & bandingin beans lintas roaster

## 3. Fitur inti (v1)
- Katalog beans publik (bahasa **English**): name, roaster, origin, process/variety, tasting notes, price, link produk
- Update **full-auto tiap hari** oleh AI dari 5 roaster -> langsung publish
- Koreksi manual oleh curator -> regenerate < 5 menit
- Search sederhana (client-side)

## 4. Nice-to-have (tunda ke v2+)
filter/sort advanced | riwayat harga + grafik | notif beans baru | admin UI | info stok

## 5. Arsitektur
- `data/beans.json` = single source of truth
- 5 roaster (terverifikasi curator, 2026-11-06):
  | Roaster | Lokasi | Situs | Mata uang |
  |---|---|---|---|
  | Prodigal | Boulder, CO, USA | getprodigal.com | USD |
  | Sey | Brooklyn, NY, USA | seycoffee.com | USD |
  | Aviary | USA | aviary.coffee | USD |
  | Tanat | Paris, France | tanat.coffee | EUR |
  | Archers | Sharjah, UAE | archerscoffee.com | AED |
- Updater = **agent AI (Hermes) via cron harian**: fetch -> ekstrak -> beans.json -> regenerate site -> push ke GitHub Pages
- Sumber utama = situs masing-masing roaster; **every.coffee** = fallback/cross-check (kelimanya terdaftar di sana)
- Koreksi = chat ke Hermes atau edit beans.json -> regenerate

## 6. Definisi selesai (v1)
- [ ] Website live di GitHub Pages (English), akses publik
- [ ] 5 roaster lengkap, data maks 24 jam
- [ ] 1 siklus full-auto jalan tanpa campur tangan
- [ ] 1 koreksi manual -> live < 5 menit

## 7. Batasan
Python | static site (GitHub Pages) | tanpa backend/login | harga tampil apa adanya per mata uang roaster (USD/EUR/AED)

## 8. Risiko & catatan lapangan
- Nama roaster mirip = mudah salah target (kasus nyata: prodigalroasters.com = Singapura vs getprodigal.com = Boulder US). Protokol: **verifikasi identitas + lokasi roaster sebelum build adapter**
- Tiap roaster beda CMS (Shopify / WooCommerce / kustom) -> satu adapter kecil per roaster; Prodigal jadi pola pertama
- **Struktur extraction bisa beda antar-fetch untuk URL yang sama** (2 varian terdeteksi di Prodigal: heading polos + "Regular price" vs link /products/ + harga polos) -> parser harus toleran keduanya; kunci = pola harga `(From )?$X USD` dan link `/products/`
- **Lineup produk bisa berubah antar fetch** (rotasi drop mingguan) -> semua snapshot diberi `last_updated`
- Harga varian ("From $X") -> simpan harga minimum + flag `from`
- seycoffee.com bisa dibaca otomatis (link produk lengkap; harga ada di halaman produk)
- Extraction kadang kepotong (lazy-load) -> cek jumlah item hasil parse vs hitungan heading

## 9. Roadmap
- **v0.1** (done): PRD final + adapter #1 Prodigal -> beans.json (data asli)
- **v0.2**: renderer HTML statis dari beans.json
- **v0.3**: adapter #2-5 + repo GitHub + deploy GitHub Pages
- **v1.0**: cron harian full-auto + siklus koreksi < 5 menit
- **v2+**: nice-to-have
