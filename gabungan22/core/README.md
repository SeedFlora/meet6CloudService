# Cloud Notes Core - praktik lokal

Folder ini berisi source Python API0.5, Dockerfile.single untuk contoh pertama, Dockerfile dengan builder/runtime, requirements.txt, dan .dockerignore. Lisensi MIT asal Lab05 dipertahankan.

Ikuti [modul lokal gabungan](../../PRAKTIKUM_GABUNGAN_22_OKTOBER.md). Semua perintah dari root repo:

```powershell
docker build -f .\gabungan22\core\Dockerfile.single -t cloud-notes-api:core-single .\gabungan22\core
docker build -t cloud-notes-api:core22 .\gabungan22\core
docker run --name cloudlab-core22 -d -p 127.0.0.1:18005:8000 -e APP_ENV=classroom cloud-notes-api:core22
```

Swagger: http://127.0.0.1:18005/docs. Data Core berada di memori proses. Compose memakai source lain di api/ dan host18006.

```powershell
docker stop cloudlab-core22
docker rm cloudlab-core22
```
