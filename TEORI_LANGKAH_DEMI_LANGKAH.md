# Docker Compose - konsep dan praktik sesuai subtopik

Gunakan [modul Compose lokal](MODUL_MAHASISWA.md) untuk urutan perintah dan [modul gabungan](PRAKTIKUM_GABUNGAN_22_OKTOBER.md) untuk Docker Core + Compose. Panduan ini menjelaskan lima subtopik praktikum dan konsep teori yang mendasarinya.

## 1. Orkestrasi beberapa container

Satu aplikasi dapat memerlukan beberapa proses. Pada Cloud Notes, API menerima HTTP, PostgreSQL menyimpan data, dan Redis menyimpan cache. Compose mendefinisikan service serta hubungan jaringan/penyimpanan dalam satu YAML, lalu menjalankannya pada satu Docker host lokal.

compose.yaml memuat services, volumes, dan konfigurasi profile. Dockerfile membangun satu image; Compose merangkai beberapa service. Build belum berarti service hidup. up membangun/menjalankan sesuai konfigurasi, ps menampilkan status, down menghentikan container project.

## 2. Service dan network

Network default dibuat otomatis untuk project cloud-notes-lab06. API memakai hostname db dan cache. Browser Windows memakai 127.0.0.1:18006 untuk API, bukan hostname internal. Port8000 adalah port API di dalam container. Port 5432/6379 tidak perlu dipublish ke host pada stack ini.

## 3. Named volume

Container dapat diganti tanpa menghapus data. PostgreSQL memakai db_data pada /var/lib/postgresql/data. Redis memakai redis_data pada /data. down mempertahankan named volume. Bukti persistensi adalah id/title catatan yang tetap ada setelah down/up, bukan hanya nama volume pada daftar.

## 4. Environment melalui .env

.env adalah file key=value lokal. POSTGRES_DB, POSTGRES_USER, dan POSTGRES_PASSWORD dipakai Compose untuk mengisi environment DB dan API. APP_ENV memberi label lingkungan API. Bentuk ${VAR:?pesan} pada compose.yaml meminta nilai wajib dan menghentikan konfigurasi sebelum startup ketika nilainya kosong. Tidak ada script penyiapan password tambahan.

Password contoh cocok untuk data latihan lokal. .env diabaikan Git; aplikasi produksi membutuhkan pengelolaan konfigurasi/credential sesuai lingkungan. Pada database lama, password tersimpan di database saat inisialisasi pertama dan tidak berubah hanya karena .env diedit.

## 5. Healthcheck, depends_on, profile, dan log

Healthcheck DB memakai pg_isready; cache memakai redis-cli ping; API meminta /health yang memeriksa DB serta Redis. depends_on service_healthy menunggu dependency siap saat startup. Kesiapan saat startup bukan jaminan service tidak akan gagal kemudian.

Profile debug menambahkan Adminer ketika dipilih. Pada contoh ini Adminer hanya alat bantu melihat tabel notes. Profile dapat digunakan untuk kelompok service dev/staging/production sesuai kebutuhan proyek; namanya tidak mengubah keamanan/deployment secara otomatis.

logs -f mengikuti keluaran proses. Ctrl+C menghentikan tampilan log tanpa menghentikan service. Buka terminal log terpisah agar terminal utama tetap dapat dipakai. Pengujian mengikuti urutan modul lokal: startup, DNS, persistensi, .env, profile, streaming log, shutdown.

## Rujukan

- [Compose quickstart](https://docs.docker.com/compose/gettingstarted/)
- [Networking](https://docs.docker.com/compose/how-tos/networking/)
- [Named volume](https://docs.docker.com/engine/storage/volumes/)
- [.env/interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)
- [Startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Profiles](https://docs.docker.com/compose/how-tos/profiles/)
