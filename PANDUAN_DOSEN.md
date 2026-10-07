# Panduan dosen Lab 06 — Compose, PostgreSQL, Redis, dan pemulihan insiden

**Durasi demo:** 90 menit. **Capaian:** mahasiswa menjalankan API + PostgreSQL + Redis sebagai satu stack, membaca network/volume/secret/healthcheck, menguji cache MISS/HIT, membuktikan data persisten, dan memulihkan gangguan cache. Repo template mandiri: `SeedFlora/meet6CloudService`. [Modul mahasiswa](MODUL_MAHASISWA.md) memuat kunci langkah dan pertanyaan.

## Persiapan sebelum kelas

1. Pastikan Docker Desktop/Engine dan Compose plugin hidup: `docker version`, `docker compose version`. Port host 8000 dan 8081 (Adminer opsional) perlu kosong. Lab 05 memakai 8000; hentikan `cloudlab-api` hanya bila itu container latihan Lab 05 yang sudah selesai.
2. Dari **root repo Lab 06**, salin `secrets/db_password.txt.example` menjadi `secrets/db_password.txt` dan `.env.example` menjadi `.env`. Di PowerShell gunakan `Copy-Item`; di Bash gunakan `cp`. File nyata diabaikan Git. Jangan tampilkan password di proyektor atau screenshot. Jangan ubah password file setelah volume database pertama kali dibuat tanpa prosedur migrasi/reset.
3. Jalankan `docker compose config --quiet`, lalu `docker compose up --build -d --wait`. `--wait` baru kembali setelah healthcheck ketiga service sehat. `docker compose ps` harus menampilkan `api`, `db`, `cache` healthy; hanya API mem-publish `127.0.0.1:8000`.
4. Jalankan `Invoke-RestMethod http://127.0.0.1:8000/health` (PowerShell) atau `curl -fsS ...` (Bash). Harapkan `status=ok`, `database=postgres`, `cache=redis`.
5. Simpan data latihan; **jangan** jalankan `docker compose down -v` jika Lab 07 akan memakai database ini. `down` biasa mempertahankan named volume.

## Alur 90 menit

| Menit | Dosen | Mahasiswa | Bukti/checkpoint |
|---:|---|---|---|
| 0–12 | Gambar alur host → API → DB/Redis, terangkan nama service. | Baca `compose.yaml`. | Tiga service, network, port hanya API. |
| 12–25 | Siapkan file lokal, `config --quiet`, `up --wait`. | Ulangi dari repo sendiri. | Tiga container healthy. |
| 25–35 | Buka Docker Desktop dan Swagger `/docs`; `getent hosts`. | Jelaskan host `db`/`cache` vs `127.0.0.1`. | DNS internal dan port host. |
| 35–50 | POST satu note, GET dua kali cepat. | Baca `X-Cache` dan data. | HTTP 201, MISS lalu HIT. |
| 50–63 | `psql SELECT`, `restart api`, `down/up` tanpa `-v`. | Cocokkan ID/judul. | Data tetap ada. |
| 63–75 | Simulasikan `stop cache`; baca health/GET; pulihkan. | Diagnosis 503 versus data 200. | Cache gagal, PostgreSQL tetap sumber data. |
| 75–83 | Aktifkan profile Adminer bila waktu cukup. | Lihat tabel `notes` tanpa password pada bukti. | UI dan API menunjuk DB sama. |
| 83–90 | Bahas lima jawaban, Git/secret, cleanup sesuai Lab 07. | Lengkapi laporan dan commit. | Tidak ada `.env`/password staged. |

## Peta berkas dan command

`compose.yaml` menetapkan `db` PostgreSQL, `cache` Redis, `api` FastAPI, dan profile `debug` untuk Adminer. `initdb/01_schema.sql` membuat tabel pada volume DB baru. `api/app/main.py` membaca secret dari `/run/secrets/db_password`, menulis catatan ke PostgreSQL, dan meng-cache daftar di Redis selama 30 detik. `api` hanya mengakses `db`/`cache` melalui DNS network Compose. Host/browser hanya mengakses API melalui `127.0.0.1:8000`; DB 5432 dan cache 6379 tidak dipublish.

PowerShell persiapan:

```powershell
Copy-Item .\secrets\db_password.txt.example .\secrets\db_password.txt
Copy-Item .\.env.example .\.env
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
```

Jika file lokal sudah ada, jangan menimpanya tanpa memeriksa volume/kredensial. Di Bash ganti `Copy-Item` dengan `cp`. `docker compose config --quiet` memeriksa bentuk konfigurasi tanpa mencetak secret. `docker compose up ... --wait` membuat image API, network, volume, dan container; dependency `service_healthy` menunggu DB/cache sebelum API start. `docker compose exec api getent hosts db cache` membuktikan DNS internal. `docker compose logs --tail=30 api db cache` memberi jejak startup/HTTP, tanpa perlu `docker exec` ke host.

## Demo cache, SQL, dan validasi

PowerShell:

```powershell
$body = '{"title":"Compose","content":"Catatan tetap ada di PostgreSQL"}'
Invoke-RestMethod http://127.0.0.1:8000/notes -Method Post -ContentType application/json -Body $body
(Invoke-WebRequest http://127.0.0.1:8000/notes -UseBasicParsing).Headers['X-Cache']
(Invoke-WebRequest http://127.0.0.1:8000/notes -UseBasicParsing).Headers['X-Cache']
try { Invoke-WebRequest http://127.0.0.1:8000/notes -Method Post -ContentType application/json -Body '{"title":"   ","content":"uji"}' -UseBasicParsing } catch { [int]$_.Exception.Response.StatusCode }
docker compose exec db psql -U clouduser -d cloudnotes -c 'SELECT id,title FROM notes;'
```

POST harus HTTP 201. Dua GET segera sesudah POST menampilkan `MISS` lalu `HIT` sebelum TTL 30 detik habis. POST menghapus cache daftar; GET pertama membaca DB dan mengisi Redis. Judul spasi saja HTTP 422 karena validator memangkas lalu menolaknya. Query SQL memperlihatkan catatan yang sama di sumber kebenaran. Jika cache tidak hidup, GET masih mengambil DB dengan `X-Cache: MISS`, tetapi dapat lebih lambat.

## Kunci insiden Redis dan persistensi

Jalankan setelah catatan dibuat. Untuk menunjukkan cache mati:

```bash
docker compose stop cache
docker compose ps
```

PowerShell membaca gejalanya:

```powershell
try { Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing } catch { [int]$_.Exception.Response.StatusCode }
$r = Invoke-WebRequest http://127.0.0.1:8000/notes -UseBasicParsing
$r.StatusCode
$r.Headers['X-Cache']
```

**Hasil kunci nyata:** health **503** karena cache dependency mati. GET notes tetap **200** dan `X-Cache: MISS`, termasuk note yang sudah dibuat; PostgreSQL masih hidup. Pada uji lokal terbaru, health dan GET masing-masing sekitar **4 detik** ketika DNS/koneksi cache gagal. Kode API melewatkan percobaan `SETEX` kedua jika `GET` Redis sudah gagal, sehingga request tidak menunggu dua kali. Ini adalah degradasi yang tetap perlu dicatat, bukan kondisi sehat penuh.

Pulihkan dengan `docker compose start cache`, `docker compose up -d --wait`, lalu GET `/health` 200 dan dua GET `/notes` cepat. Berikutnya:

```bash
docker compose restart api
docker compose --profile debug down
docker compose up -d --wait
docker compose exec db psql -U clouduser -d cloudnotes -c 'SELECT id,title FROM notes;'
docker compose ps
```

`restart api` tidak menghapus volume. `down` menghapus container/jaringan, tetapi **tidak** named volume; `up` membuat container baru yang memasang volume yang sama. Pada uji ini note ID 1 tetap ada setelah restart maupun down/up, dan SQL menunjukkan tiga note total (termasuk note dari uji integrasi lain). Jumlah total dapat berbeda pada kelas. **Jangan tambahkan `-v`** kecuali memang ingin menghapus data latihan dan tidak ada lab berikutnya yang memakainya.

**Bonus diagnosis isi cache rusak:** ketika stack kembali sehat, jalankan `docker compose exec -T cache redis-cli SET notes:list '{broken'` pada Redis lab ini saja. GET `/notes` pertama harus 200/MISS dari PostgreSQL; API menghapus nilai JSON rusak dan mengisi ulang cache. GET kedua 200/HIT. `/health` tetap 200 karena koneksi Redis sehat. Kasus ini membedakan gangguan **isi cache** dari gangguan **service cache**. Sudah diuji pada stack target, note ID 1 tetap ada.

## Screenshot dan penjelasan command pada tiap gambar

![Persiapan dan validasi konfigurasi tanpa membuka password](screenshots/lab06_persiapan_config.png)

**Perintah:** `Test-Path .env`, `Test-Path secrets/db_password.txt`, `docker compose config --quiet`, `git check-ignore -v .env secrets/db_password.txt`. **Fungsi:** cek file lokal, bentuk Compose, dan perlindungan Git. **Cara kerja:** Compose membaca konfigurasi tanpa mencetaknya; Git melaporkan aturan ignore. **Baca:** dua `True`, exit 0, dua aturan ignore. Ini render output command aktual.

![DNS Compose, log, dan HTTP health](screenshots/lab06_dns_log_health.png)

**Perintah:** `docker compose exec -T api getent hosts db cache`, `docker compose logs --tail=4 api db cache`, `curl.exe -s -i http://127.0.0.1:8000/health`. **Fungsi:** bukti service name, jejak startup/request, dan health. **Cara kerja:** DNS internal menerjemahkan `db`/`cache`; API memberi 200 jika dependency hidup. **Baca:** dua alamat internal, log tiga service, HTTP 200 dan JSON sehat. IP dapat berubah. Ini render output command aktual.

![Repo template Lab 06 telah terbit](screenshots/lab06_git_terbit.png)

*SHA pada gambar adalah snapshot saat uji. Setelah modul diperbarui, jalankan ulang perintah untuk memeriksa commit terbaru.*

**Perintah:** `git remote -v`, `git status --short`, `git log -1`, `git rev-parse HEAD`, `git ls-remote origin refs/heads/main`. **Fungsi:** memeriksa repo tujuan dan hasil publikasi. **Cara kerja:** SHA lokal dan remote dibandingkan. **Baca:** `Sama: True` pada repo template dosen; mahasiswa mengulanginya pada repo pribadi. Ini render output command aktual.

![Docker Desktop dengan tiga container Lab 06 aktif](screenshots/00_docker_desktop.jpg)

**Perintah:** `docker compose up --build -d --wait`, `docker compose ps`, lalu buka Docker Desktop > Containers. **Fungsi:** memadankan kondisi CLI dengan UI. **Cara kerja:** Compose menjalankan `api`, `db`, `cache` pada network internal; API saja meneruskan port host 8000. **Baca:** tiga titik hijau berarti container berjalan; terminal harus menulis healthy untuk healthcheck. DB/cache tidak punya mapping port host.

![Tiga service pada output Compose awal](screenshots/lab06_compose.png)

**Perintah:** `docker compose ps`. **Fungsi:** memeriksa service dan port. **Cara kerja:** Compose menanyakan status Docker. **Baca:** `api`, `db`, `cache` healthy; API port 8000.

![OpenAPI dari stack awal](screenshots/lab06_api_docs.png)

**Perintah:** buka `http://127.0.0.1:8000/docs`. **Fungsi:** mengenali route aplikasi. **Cara kerja:** FastAPI menyajikan Swagger UI. **Baca:** health, notes, DELETE.

![Cache MISS dan HIT](screenshots/lab06_cache.png)

**Perintah:** POST note, lalu dua GET `/notes`. **Fungsi:** membuktikan Redis dipakai untuk daftar. **Cara kerja:** GET pertama mengambil DB dan mengisi cache; GET kedua membaca Redis. **Baca:** `X-Cache: MISS` lalu `HIT` dengan isi data sama.

![Data sebelum dan sesudah restart](screenshots/lab06_persistence.png)

**Perintah:** `psql SELECT`, `docker compose restart api`, `down`/`up`, ulangi SELECT. **Fungsi:** membuktikan volume database. **Cara kerja:** container diganti tetapi `db_data` tetap. **Baca:** ID/judul sama.

![Adminer login aman](screenshots/lab06_adminer.png)

**Perintah:** `docker compose --profile debug up -d adminer`, buka `http://127.0.0.1:8081`. **Fungsi:** inspeksi DB lewat UI. **Cara kerja:** Adminer terkoneksi ke hostname `db` pada network Compose. **Baca:** database `cloudnotes`; jangan tampilkan password pada bukti.

![Tabel notes di Adminer](screenshots/lab06_adminer_notes.png)

**Perintah:** pilih tabel `notes` dan **Select data**. **Fungsi:** membandingkan hasil API/SQL/UI. **Cara kerja:** Adminer menjalankan SELECT ke PostgreSQL yang sama. **Baca:** ID/judul sama; jangan klik Drop/Truncate.

![Uji ulang cache dan validasi](screenshots/lab06_uji_terkini.png)

**Perintah:** `up --wait`, POST, dua GET, POST judul spasi. **Fungsi:** bukti run terbaru. **Cara kerja:** output Docker/API aktual ditata agar terbaca. **Baca:** healthy, 201, MISS→HIT, 422.

![OpenAPI yang berjalan kembali](screenshots/lab06_docs_live_terkini.png)

**Perintah:** buka `/docs` pada port 8000. **Fungsi:** membuktikan route live, termasuk DELETE. **Cara kerja:** Chrome lokal memuat halaman API. **Baca:** versi 0.6 dan endpoint yang tersedia.

![Insiden cache dan data persisten](screenshots/lab06_incident_persistensi_terkini.png)

**Perintah:** stop cache, cek health/notes, start cache, restart API, down/up tanpa `-v`, query SQL. **Fungsi:** bukti diagnosis dan pemulihan. **Cara kerja:** catatan tetap di volume PostgreSQL saat service cache/API berganti. **Baca:** health 503 saat outage, GET 200/MISS, ID tetap ada sesudah pemulihan. Transkrip aktual ditata ulang; angka waktu dapat berbeda.

![Cache JSON rusak dipulihkan dari DB](screenshots/lab06_cache_corrupt_terkini.png)

**Perintah:** `docker compose exec -T cache redis-cli SET notes:list '{broken'` dan dua GET `/notes`. **Fungsi:** menguji ketahanan saat data cache rusak. **Cara kerja:** API menangkap error parse, membuang cache rusak, mengambil PostgreSQL, lalu menulis salinan sehat. **Baca:** 200/MISS di request pertama, 200/HIT di kedua; health tetap 200 karena Redis hidup.

## Kunci analisis, masalah umum, dan pengumpulan

1. `DB_HOST=db` berlaku dalam DNS Compose; browser host memanggil `127.0.0.1:8000` yang dipublish API.
2. `restart api` mengganti proses; `down` mengganti container/jaringan; volume tetap. `down -v` juga menghapus volume dan data latihan.
3. POST/DELETE menghapus cache daftar; GET pertama MISS dan mengisi Redis selama 30 detik; GET berikutnya HIT sampai TTL habis atau data berubah.
4. `depends_on: service_healthy` menunda startup awal API, tetapi tidak menjamin dependency tidak akan gagal kemudian. Saat Redis mati, health 503 dan GET fallback ke DB.
5. `.env.example` dan secret contoh boleh ada di Git; `.env` dan `secrets/db_password.txt` nyata harus lokal. Cek `git check-ignore -v .env secrets/db_password.txt` di repo pribadi sebelum commit.

| Gejala | Diagnosis/aksi |
|---|---|
| Port 8000 dipakai | `docker ps`; hentikan container Lab 05 sendiri bila selesai. |
| API masih `starting` | Gunakan `up --wait`, baca `docker compose logs --tail=50 api db cache`. |
| Password DB gagal setelah file diubah | Volume lama menyimpan password lama; jangan hapus volume yang berisi pekerjaan. Cocokkan kredensial atau lakukan reset data latihan dengan izin jelas. |
| Dua GET sama-sama MISS | Jalankan berurutan dalam 30 detik; POST di antaranya memang menghapus cache. |
| Health 503 tetapi notes 200 | Cache mungkin mati; cek `docker compose ps` dan log. |
| Adminer masih hidup setelah cleanup | Gunakan `docker compose --profile debug down`. |

Laporan `hasil/lab06.md` dibuat dari `hasil/TEMPLATE_LAPORAN.md`, bukti pribadi di `hasil/bukti/`. Cek `git status`, `git diff --check`, `git add compose.yaml api initdb secrets .env.example hasil/lab06.md hasil/bukti`, `git diff --cached --name-only`, dan `git diff --cached --check` sebelum commit/push. Jangan menempelkan password di SQL/screenshot. **Teruji pada komputer ini:** config Compose, build, tiga service healthy, OpenAPI browser, HTTP health/POST/GET/422, MISS/HIT, fallback saat Redis mati, cache JSON rusak, pemulihan, restart API, down/up tanpa volume hapus, SQL persistence. Stack dikembalikan healthy setelah uji.
