# Cloud Notes API 0.5 untuk tahap Docker Core, 22 Oktober 2026

Folder ini adalah build context mandiri untuk API yang menyimpan catatan di memori proses. Dockerfile, `.dockerignore`, `requirements.txt`, dan `app/` disalin tanpa perubahan dari materi [Lab 05](https://github.com/SeedFlora/meet5CloudService). Hak cipta dan lisensi MIT asli dipertahankan di [LICENSE](LICENSE).

Ikuti [modul praktikum gabungan](../../PRAKTIKUM_GABUNGAN_22_OKTOBER.md). Jalankan perintah dari **root repo meet6CloudService**, bukan dari folder ini:

```bash
docker build -t cloud-notes-api:core22 ./gabungan22/core
docker run --name cloudlab-core22 -d -p 127.0.0.1:18005:8000 -e APP_ENV=classroom cloud-notes-api:core22
```

Buka `http://127.0.0.1:18005/docs`. API versi 0.5 memiliki `/health`, `/runtime`, GET/POST `/notes`, dan GET `/notes/{note_id}`. Data hilang ketika proses API dibuat ulang. Host port 18005 diteruskan ke port 8000 container agar berbeda dengan tahap Compose di root repo yang memakai host port 8000.

Tahap ini tidak memakai PostgreSQL atau Redis. Tahap Compose memakai kode API versi 0.6 di `api/`, bukan folder ini. Jangan mengganti Dockerfile atau Compose di root repo dengan file tahap Core.
