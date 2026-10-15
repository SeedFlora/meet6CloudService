# Docker Core dan Docker Compose - praktikum lokal

**Mulai dari [modul gabungan lokal 22 Oktober](PRAKTIKUM_GABUNGAN_22_OKTOBER.md)** atau [PDF](PRAKTIKUM_GABUNGAN_22_OKTOBER.pdf). [Slide gabungan](slides/LAB_GABUNGAN_DOCKER_CORE_COMPOSE_22_OKTOBER.pptx) mengikuti urutan yang sama.

Windows + Docker Desktop + PowerShell. Satu clone menyediakan Core dan Compose. Jalur utama berupa perintah Docker/Compose langsung. Tidak memakai helper instalasi atau Codespaces. Internet diperlukan untuk download awal; seluruh service aplikasi berjalan lokal. Docker Hub dibahas pada subtopik registry dan memerlukan akun/Internet sendiri.

| Praktik | Source | Port Windows | Konfigurasi |
|---|---|---|---|
| Core | gabungan22/core | 18005 | -e APP_ENV=classroom |
| Compose API + PostgreSQL + Redis | api + compose.yaml | 18006 | .env |
| Adminer profile debug | compose.yaml | 18061 | .env untuk password DB |

## Modul sesuai subtopik

- [Docker Core + Compose, langkah lengkap](PRAKTIKUM_GABUNGAN_22_OKTOBER.md)
- [Docker Compose saja](MODUL_MAHASISWA.md) dan [PDF](MODUL_MAHASISWA.pdf)
- [Konsep Compose sesuai RPS](TEORI_LANGKAH_DEMI_LANGKAH.md) dan [PDF](TEORI_LANGKAH_DEMI_LANGKAH.pdf)
- [Pindah dari modul lama](MIGRASI_MODUL_LAMA.md)

## Memulai pada clone baru

Buka Docker Desktop sampai Engine running, lalu dari PowerShell pada folder kerja baru:

```powershell
git clone https://github.com/SeedFlora/meet6CloudService.git meet6CloudService-local
cd .\meet6CloudService-local
Copy-Item .\.env.example .\.env
docker compose config --quiet
docker compose up --build -d --wait
docker compose ps
Invoke-RestMethod http://127.0.0.1:18006/health
```

Hasil health wajib memuat **database postgres dan cache redis**, lalu buka http://127.0.0.1:18006/docs. Persiapan Core dan penjelasan tiap perintah ada di modul gabungan. Copy .env dilakukan pada clone baru; gunakan konfigurasi yang sudah benar pada pengulangan. File secret tidak dipakai dalam revisi ini.

Selesai:

```powershell
docker compose --profile debug down
```

Volume database tetap disimpan. Project/volume lama tetap dipertahankan; password database yang telah diinisialisasi harus cocok dengan .env.

**Kebijakan kelas:** latihan formatif untuk satu proyek kelompok 3 orang; presentasi checkpoint minggu 7 dan hasil akhir minggu 14. Bobot mengikuti RPS/LMS. Tidak ada tugas/nilai tambahan per lab.

Screenshot dan slide lama yang tidak ditautkan pada daftar modul di atas adalah arsip versi terdahulu. Gunakan perintah dan port pada revisi lokal ini. Lisensi source tetap [MIT](LICENSE).
