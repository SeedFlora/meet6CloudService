# Sumber gambar tahap Docker Core

Kelima gambar berikut disalin tanpa perubahan dari `screenshots/` materi [Lab 05](https://github.com/SeedFlora/meet5CloudService). Bukti tersebut berasal dari pengujian materi sebelumnya; bukan screenshot baru pelaksanaan 22 Oktober 2026.

| Berkas | Isi gambar | Perbedaan terhadap praktikum gabungan |
|---|---|---|
| `lab05_dockerfile_persiapan.png` | Pemeriksaan Docker dan instruksi Dockerfile | Source Dockerfile sama; pada praktikum gabungan path build context adalah `gabungan22/core`. |
| `lab05_build.png` | Image, runtime `appuser`, UID 10001, dan mapping port | Gambar memakai tag `lab05`, nama `cloudlab-api`, host port 8000. Praktikum gabungan memakai tag `core22`, nama `cloudlab-core22`, host port 18005. Port container tetap 8000. |
| `lab05_openapi.png` | Swagger UI API versi 0.5 | Endpoint sama; alamat browser praktikum gabungan `http://127.0.0.1:18005/docs`. |
| `lab05_api.png` | Health, runtime, POST, dan GET API memori | Perintah praktikum gabungan menuju host port 18005. Tampilan GET pada gambar merupakan penyajian objek oleh PowerShell; body HTTP GET `/notes` adalah JSON array. |
| `lab05_validation_reset.png` | Input ditolak HTTP 422 dan data kosong setelah proses/container diganti | Gambar asal memakai rm/run; sesi utama gabungan memakai restart `cloudlab-core22` pada host port 18005. Keduanya memulai proses API baru sehingga dictionary memori kosong. |

Gambar terminal berlatar gelap menata ulang keluaran pengujian aktual agar teks terbaca. `lab05_openapi.png` adalah screenshot antarmuka browser dari API yang dijalankan. Caption pada modul gabungan menjelaskan command, fungsi, proses, dan keluaran yang perlu diamati pada mesin peserta.
