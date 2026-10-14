# Lab 06 — Docker Compose: API + PostgreSQL + Redis

## Praktikum gabungan 22 Oktober 2026

Mulai dari [modul Docker Core dan Docker Compose](PRAKTIKUM_GABUNGAN_22_OKTOBER.md), [PDF modul](PRAKTIKUM_GABUNGAN_22_OKTOBER.pdf), dan [slide praktikum gabungan](slides/LAB_GABUNGAN_DOCKER_CORE_COMPOSE_22_OKTOBER.pptx). Paket ini dipakai untuk BA75 dan BB75 selama 100 menit: Core 25 menit, Compose 60 menit, serta refleksi dan cleanup 15 menit. Siapkan clone, Docker Engine, dan build pertama sebelum kelas.

Satu clone repo ini menyediakan dua tahap Cloud Notes. API Core di `gabungan22/core/` memakai memori dan port host **18005**. Stack Compose dari root repo memakai PostgreSQL, Redis, dan port API **8000**. Catatan Core tidak berpindah otomatis ke database Compose. Panduan menjelaskan fungsi perintah, hasil yang diharapkan, dan gambar dari praktik sebelumnya. Adminer serta simulasi gangguan cache menjadi latihan tambahan bila waktu cukup.

<!-- lecture-materials:start -->

## Materi teori sebelum praktikum

- [Pertemuan 06: Docker Compose](slides/Teori_Pertemuan_06.pptx)
- [Panduan teori langkah demi langkah dengan screenshot](TEORI_LANGKAH_DEMI_LANGKAH.md)
- [PDF panduan teori](TEORI_LANGKAH_DEMI_LANGKAH.pdf)

Slide menghubungkan konsep, kasus kerja, bacaan/video resmi, dan langkah lab.

Urutan belajar: baca slide teori, ikuti panduan teori dari persiapan sampai pemulihan, kemudian kerjakan checkpoint pada modul praktikum. Backup tambahan memakai database uji baru sehingga catatan sumber tetap tersedia.

<!-- lecture-materials:end -->

**Kebijakan kelas:** Lab ini latihan formatif, tanpa tugas, nilai, atau penyerahan terpisah. Satu proyek besar dikerjakan oleh kelompok **3 orang**, dengan presentasi checkpoint minggu 7 (UTS) dan hasil akhir minggu 14 (UAS). Simpan hasil lab hanya bila berguna sebagai referensi atau bukti proses proyek. Baca [brief proyek kelompok](PROYEK_KELOMPOK.md). Bobot resmi tetap mengikuti RPS/LMS.

Repo template: [SeedFlora/meet6CloudService](https://github.com/SeedFlora/meet6CloudService). [Modul mahasiswa](MODUL_MAHASISWA.md) memuat screenshot, kunci gangguan Redis, dan jawaban analisis; [panduan Git](PANDUAN_GIT.md) dipakai dari root repo pribadi. Versi cetak: [PDF mahasiswa](MODUL_MAHASISWA.pdf). Slide kelas ada di `slides/`.

**Capaian:** menjalankan tiga service pada network Compose, memakai nama service sebagai hostname, menunggu healthcheck, menyimpan data di volume, membaca secret dari file, dan memakai profile debug. Ini kelanjutan API Lab 05; `notes` sekarang persisten.

## Jalankan

Dari root repo Lab 06, siapkan password lokal. File nyata diabaikan Git.

PowerShell:

```powershell
Copy-Item .\secrets\db_password.txt.example .\secrets\db_password.txt
Copy-Item .\.env.example .\.env
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
```

Bash/WSL:

```bash
cp secrets/db_password.txt.example secrets/db_password.txt
cp .env.example .env
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
curl -fsS http://127.0.0.1:8000/health
```

Ubah isi password contoh sebelum memakai proyek di luar laptop. Secret dipasang sebagai file `/run/secrets/db_password` di service DB dan API. Nama host `db` dan `cache` hanya berlaku di network Compose; dari host gunakan `127.0.0.1:8000` untuk API.

## Eksperimen

PowerShell:

```powershell
$body = '{"title":"Compose","content":"Database tetap ada setelah API dibuat ulang."}'
Invoke-RestMethod http://127.0.0.1:8000/notes -Method Post -ContentType application/json -Body $body
(Invoke-WebRequest http://127.0.0.1:8000/notes -UseBasicParsing).Headers['X-Cache']
(Invoke-WebRequest http://127.0.0.1:8000/notes -UseBasicParsing).Headers['X-Cache']
docker compose restart api
Invoke-RestMethod http://127.0.0.1:8000/notes
```

Bash:

```bash
curl -fsS -X POST http://127.0.0.1:8000/notes -H 'Content-Type: application/json' -d '{"title":"Compose","content":"Database tetap ada setelah API dibuat ulang."}'
curl -i http://127.0.0.1:8000/notes
curl -i http://127.0.0.1:8000/notes
docker compose restart api
curl -fsS http://127.0.0.1:8000/notes
```

Header `X-Cache` pertama `MISS`, berikutnya `HIT` dalam 30 detik. Restart API tidak menghapus catatan. Lihat konektivitas dan volume:

```bash
docker compose exec api getent hosts db cache
docker compose exec db psql -U clouduser -d cloudnotes -c 'SELECT id, title FROM notes;'
docker compose logs --tail=30 api db cache
docker compose --profile debug up -d adminer
```

Adminer opsional di `http://127.0.0.1:8081` (system PostgreSQL, server `db`, user `clouduser`, password dari file secret, database `cloudnotes`). Jangan menempelkan password dalam laporan.

## Diskusi dan bersih-bersih

- Bandingkan `depends_on: service_healthy` dengan urutan start biasa.
- Jelaskan perbedaan `docker compose down` (volume tetap) dan `docker compose down -v` (data hilang). Jalankan `-v` hanya jika data latihan boleh dihapus.
- Bukti: endpoint `health`, dua nilai `X-Cache`, query SQL, dan penjelasan network/volume.

```bash
docker compose --profile debug down
```

Perintah ini juga menghentikan Adminer bila profile `debug` sempat diaktifkan. Tanpa Adminer, perintah yang sama tetap menghentikan service utama. Volume database tetap dipertahankan; tambahkan `-v` hanya jika data latihan boleh dihapus.

**Git opsional:** commit `compose.yaml`, source, `.env.example`, dan file secret contoh. Pastikan `git status` tidak menampilkan `.env` atau `secrets/db_password.txt` sebelum push.

Rujukan: [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/), [Compose profiles](https://docs.docker.com/compose/how-tos/profiles/), [Compose secrets](https://docs.docker.com/compose/how-tos/use-secrets/).
