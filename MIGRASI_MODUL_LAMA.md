# Berpindah ke modul lokal revisi 15 Oktober 2026

Jalur baru memakai satu file .env, API host18006, dan Adminer host18061. File secrets/db_password.txt tidak digunakan lagi. Folder/file secret lama tetap dapat disimpan sebagai arsip; tidak perlu dihapus atau diperbaiki untuk menjalankan konfigurasi baru.

## Jalur yang dipakai di kelas

1. Simpan pekerjaan/berkas latihan lama.
2. Buka PowerShell pada folder induk pilihan sendiri.
3. Clone repo ke folder baru seperti petunjuk modul lokal.
4. Salin .env.example menjadi .env pada clone baru.
5. Jalankan docker compose config --quiet, lalu docker compose up --build -d --wait.
6. Gunakan http://127.0.0.1:18006/docs untuk Compose; port 18005 untuk Core.

Project Compose tetap bernama cloud-notes-lab06. Nama volume db_data dan redis_data dipertahankan agar data latihan lama tidak dihapus. Password contoh baru sama dengan contoh kelas sebelumnya. Database yang sudah diinisialisasi dengan password sendiri memerlukan POSTGRES_PASSWORD pada .env yang sesuai dengan password awal database itu. Mengubah file konfigurasi tidak mengganti password PostgreSQL yang sudah tersimpan.

Untuk database lama dengan password khusus, isi POSTGRES_PASSWORD pada .env lokal dengan password tersebut sebelum up. Pengajar/pemilik data memeriksa konfigurasi lama secara lokal; tidak perlu mengirim password melalui chat atau screenshot. Tidak ada perintah reset database atau penghapusan volume dalam migrasi ini.

## Container Core lama pada port 8000

Core lama dapat tetap menjawab /health di port 8000 walaupun Compose gagal. Respons Core adalah status ok dan service cloud-notes-api. Compose revisi dibuka di port 18006 dan harus mengembalikan status ok, database postgres, cache redis. Dengan port berbeda, pemeriksaan tidak tertukar.

Periksa container dengan docker ps. Hentikan container latihan lama milik sendiri setelah tidak dipakai. Tidak perlu menghentikan semua container komputer.

## Materi yang dipakai

- [Modul Docker Core + Compose lokal](PRAKTIKUM_GABUNGAN_22_OKTOBER.md)
- [Modul Compose lokal](MODUL_MAHASISWA.md)
- [PDF gabungan](PRAKTIKUM_GABUNGAN_22_OKTOBER.pdf)

Screenshot pada folder screenshots dan gabungan22/screenshots berasal dari versi sebelumnya, dengan port/konfigurasi lama. Screenshot tersebut adalah arsip bukti, bukan langkah untuk revisi lokal ini.
