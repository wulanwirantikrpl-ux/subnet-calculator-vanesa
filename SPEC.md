# SPEC — SubnetEDU: Kalkulator Subnet & VLSM

## Tujuan
Membangun aplikasi web satu halaman untuk guru dan siswa TKJ guna menghitung subnet IPv4 serta membagi sebuah network menjadi beberapa subnet dengan metode VLSM.

## Aturan Validasi
- IPv4 harus terdiri dari tepat empat oktet, setiap oktet 0–255.
- Tidak boleh ada spasi dan angka nol di depan, misalnya `192.168.01.1` ditolak.
- Prefix harus bilangan bulat 0–32.
- Input tidak valid menghasilkan `ValueError` pada fungsi dan HTTP 400 pada API.
- Network VLSM harus berupa alamat network IPv4/CIDR yang valid.
- Kebutuhan host harus berupa daftar tidak kosong berisi bilangan bulat minimal 1.

## Kontrak Fungsi
### `hitung_subnet(ip: str, prefix: int) -> dict`
Menghasilkan `mask`, `network`, `broadcast`, `first_host`, `last_host`, `usable_hosts`.
- Prefix 0–30: jumlah host `2^(32-prefix)-2`.
- `/31`: point-to-point sesuai RFC 3021, 2 host, broadcast `None`.
- `/32`: 1 host, broadcast `None`, first dan last host sama dengan IP.
- Network dihitung dengan operasi bitwise AND antara IP dan subnet mask.

### `alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]`
- Urutkan kebutuhan terbesar ke terkecil.
- Ukuran blok adalah pangkat dua terkecil yang memenuhi kebutuhan host + 2, minimum `/30`.
- Tiap hasil memuat `kebutuhan`, `network_cidr`, dan semua kunci hasil `hitung_subnet`.
- Tolak network bukan alamat network, daftar kosong/nilai host kurang dari 1, atau kapasitas network tidak mencukupi.

## Kontrak API
- `GET /api/subnet?ip=&prefix=`
- `POST /api/vlsm` dengan JSON `{ "network": "...", "kebutuhan_host": [...] }`
- `GET /` menyajikan halaman web.
- Kesalahan input mengembalikan HTTP 400 dengan field `detail`.

## Halaman Web
Satu halaman responsif dengan dua mode: Subnet dan VLSM. Hasil perhitungan dan pesan kesalahan ditampilkan secara jelas.

## Tabel Test Case
| Kasus | Input | Hasil yang diharapkan |
|---|---|---|
| Subnet umum | `172.16.5.130/25` | Network `.128`, broadcast `.255`, 126 host |
| Subnet /30 | `10.0.0.0/30` | Host `.1`–`.2`, broadcast `.3`, 2 host |
| Point-to-point | `192.168.1.0/31` | 2 host, tanpa broadcast |
| Single host | `192.168.1.5/32` | 1 host, tanpa broadcast |
| Oktet salah | `256.1.1.1/24` | Ditolak |
| Leading zero | `192.168.01.1/24` | Ditolak |
| Prefix salah | Prefix 33 atau -1 | Ditolak |
| VLSM | `192.168.1.0/24`, `[100,50,20,2]` | `/25`, `/26`, `/27`, `/30` berturut-turut |
| VLSM tidak cukup | `192.168.1.0/24`, `[200,100]` | Ditolak |

## Di Luar Cakupan
Autentikasi pengguna, penyimpanan riwayat perhitungan, konfigurasi perangkat jaringan, dan pemindaian jaringan.
