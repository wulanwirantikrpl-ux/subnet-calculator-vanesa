# [Feature] Kalkulator Subnet

## Deskripsi
Menyediakan perhitungan detail subnet IPv4 berdasarkan alamat IP dan prefix.

## Tugas
- Membuat fungsi hitung_subnet.
- Menyediakan endpoint GET /api/subnet.
- Menghubungkan form pada halaman web dengan API.
- Menangani input IPv4 dan prefix yang tidak valid.

## Kriteria Penerimaan
- Kasus uji pada SPEC.md untuk /25, /30, /31, /32 lulus.
- IPv4 invalid dan prefix di luar 0–32 ditolak.
- Halaman utama dapat diakses melalui GET /.

## Alur Kerja
Issue → branch → test dulu → implementasi → commit → pull request → CI → merge.
