# SubnetEDU — Kalkulator Subnet & VLSM

Aplikasi web untuk membantu pembelajaran subnetting IPv4 dan Variable Length Subnet Masking (VLSM). Dibangun dengan Python 3.12, FastAPI, HTML, CSS, dan JavaScript.

## Fitur
- Kalkulator subnet IPv4 dengan prefix `/0` sampai `/32`.
- Menampilkan subnet mask, network address, broadcast address, first host, last host, dan jumlah host.
- Penanganan khusus `/31` sesuai RFC 3021 dan `/32` sebagai satu alamat host.
- Validasi IPv4 ketat: empat oktet, rentang 0–255, tanpa spasi dan tanpa nol di depan.
- Alokasi VLSM dari kebutuhan host terbesar ke terkecil.
- API JSON dan tampilan responsif.
- Unit test pytest, smoke test, dan konfigurasi Docker serta GitHub Actions.

## Persyaratan
- Python 3.12
- pip
- (Opsional) Docker Desktop untuk menjalankan container

## Menjalankan secara lokal
```bash
# Windows PowerShell atau terminal
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
uvicorn main:app --reload
```
Buka `http://127.0.0.1:8000`.

Alternatif jika menggunakan uv:
```bash
uv sync --dev
uv run fastapi dev main.py
```

## API
- `GET /api/subnet?ip=172.16.5.130&prefix=25`
- `POST /api/vlsm` dengan body JSON:
```json
{
  "network": "192.168.1.0/24",
  "kebutuhan_host": [100, 50, 20, 2]
}
```
- `GET /docs` untuk dokumentasi Swagger interaktif.

## Menjalankan test
```bash
pytest -v
pytest test_main.py -v --cov=main --cov-report=term-missing
```

## Docker
Build image:
```bash
docker build -t subnet-calculator .
```
Jalankan container:
```bash
docker run -d --name subnet-app -p 8000:8000 subnet-calculator
```
Smoke test:
```bash
python scripts/smoke_test.py http://127.0.0.1:8000
```
Hentikan dan hapus container:
```bash
docker rm -f subnet-app
```

## Struktur folder
```text
subnet-calculator-sqa/
├── .github/workflows/ci.yml
├── issues/
├── scripts/smoke_test.py
├── static/
│   ├── app.js
│   └── style.css
├── main.py
├── index.html
├── test_main.py
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Catatan Vibe Engineering
Urutan kerja yang disarankan: memahami masalah dan edge case → menetapkan aturan pada `SPEC.md` → desain UI → menulis test lebih dahulu → implementasi → review → Git/CI → Docker → deployment. Keputusan khusus `/31` dan `/32` ditulis eksplisit agar hasil dapat diperiksa, bukan hanya terlihat berjalan.
