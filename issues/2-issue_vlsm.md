# [Feature] VLSM Allocator

## Deskripsi
Menyediakan pembagian sebuah network menjadi beberapa subnet sesuai kebutuhan host.

## Tugas
- Membuat fungsi alokasi_vlsm.
- Menyediakan endpoint POST /api/vlsm.
- Mengurutkan kebutuhan host dari terbesar ke terkecil.
- Menampilkan hasil alokasi pada tabel di halaman web.

## Kriteria Penerimaan
- Input 192.168.1.0/24 dengan kebutuhan 100, 50, 20, 2 menghasilkan /25, /26, /27, /30.
- Network yang tidak valid dan kapasitas yang tidak cukup ditolak.
- Seluruh test VLSM pada test_main.py lulus.

## Alur Kerja
Issue → branch → test dulu → implementasi → commit → pull request → CI → merge.
