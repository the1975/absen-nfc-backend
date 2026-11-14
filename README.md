## Database

```sql
CREATE TABLE IF NOT EXISTS kartu (
  uid    VARCHAR(20) PRIMARY KEY,
  npm    VARCHAR(20) NULL,
  nama   VARCHAR(40) NOT NULL,
  dibuat DATETIME NOT NULL,
  INDEX (npm)
);

CREATE TABLE IF NOT EXISTS absen (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  uid    VARCHAR(20) NOT NULL,
  npm    VARCHAR(20) NULL,
  nama   VARCHAR(40) NOT NULL,
  status VARCHAR(10) NOT NULL,
  waktu  DATETIME NOT NULL,
  INDEX (waktu)
);
```

**UID bukan NPM.** UID adalah nomor seri dari pabrik chip (8, 14, atau 20 karakter heksadesimal) dan tidak bisa diganti di kartu biasa. Karena itu tabel `kartu` memetakan UID ke NPM. NPM disimpan sebagai teks, bukan angka, supaya nol di depan tidak hilang dan tidak kena batas ukuran bilangan bulat.

## API

| Metode | Alamat | Fungsi |
|---|---|---|
| POST | `/tap` | Dipanggil ESP32: cek UID, catat absen, balas izin atau tolak |
| GET | `/kartu` | Daftar kartu |
| POST | `/kartu` | Daftarkan atau ubah kartu (`uid`, `nama`, `npm` opsional) |
| DELETE | `/kartu/{uid}` | Hapus kartu |
| GET | `/absen` | 50 riwayat terakhir |
| POST | `/absen` | Catat absen manual |
| GET | `/dashboard` | Halaman beranda |
| GET | `/dashboard/kartu` | Halaman kelola kartu |

Contoh:

```bash
curl -X POST localhost:8000/tap -H "Content-Type: application/json" -d '{"uid":"AABBCCDD"}'
```

## Struktur folder

```
absen-nfc-backend/
├── esp32/
│   └── absen_nfc.ino        # sketsa ESP32 (Wokwi)
├── server/
│   ├── main.py              # rute API dan dashboard
│   ├── db.py                # koneksi MySQL (pengaturan dari .env)
│   ├── skema.sql            # skema tabel, dibuat otomatis saat server mulai
│   ├── migrasi_sqlite.py    # pindah data lama dari SQLite ke MySQL
│   ├── requirements.txt
│   └── templates/           # halaman dashboard (Jinja2 + htmx)
├── mulai_db.sh              # menyalakan MariaDB
├── mulai_server.sh          # menyalakan database dan server
├── mulai_tunnel.sh          # membuka tunnel dan menampilkan alamatnya
└── .env.example             # contoh pengaturan database
```

## Menjalankan

Prasyarat: Python 3.12 dan MariaDB atau MySQL. Skrip `mulai_*.sh` ditulis untuk lingkungan Alpine (terminal Acode di Android). Di lingkungan lain, nyalakan database dengan cara biasa lalu jalankan servernya.

1. Ambil kode dan pasang kebutuhan:

```bash
git clone https://github.com/the1975/absen-nfc-backend.git
cd absen-nfc-backend
pip install -r server/requirements.txt
cp .env.example .env
```

2. Buat database dan pengguna, lalu isi sandinya di `.env`:

```sql
CREATE DATABASE absen_nfc CHARACTER SET utf8mb4;
CREATE USER 'absen'@'localhost' IDENTIFIED BY 'ganti_sandi';
GRANT ALL PRIVILEGES ON absen_nfc.* TO 'absen'@'localhost';
```

| Variabel `.env` | Isi |
|---|---|
| `DB_SOCKET` | Jalur soket MySQL (kalau diisi, dipakai dibanding host dan port) |
| `DB_HOST`, `DB_PORT` | Alamat database kalau tidak lewat soket |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Pengguna, sandi, dan nama database |

3. Nyalakan database dan server (tabel dibuat otomatis):

```bash
./mulai_server.sh
```

4. Buka `http://localhost:8000/dashboard`, lalu daftarkan kartu di halaman Kartu.
5. Untuk Wokwi: jalankan `./mulai_tunnel.sh`, salin alamat yang muncul ke `URL_DASAR` di sketsa, lalu jalankan simulasi dan tempelkan kartu.

## Database

```sql
CREATE TABLE IF NOT EXISTS kartu (
  uid    VARCHAR(20) PRIMARY KEY,
  npm    VARCHAR(20) NULL,
  nama   VARCHAR(40) NOT NULL,
  dibuat DATETIME NOT NULL,
  INDEX (npm)
);

CREATE TABLE IF NOT EXISTS absen (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  uid    VARCHAR(20) NOT NULL,
  npm    VARCHAR(20) NULL,
  nama   VARCHAR(40) NOT NULL,
  status VARCHAR(10) NOT NULL,
  waktu  DATETIME NOT NULL,
  INDEX (waktu)
);
```

**UID bukan NPM.** UID adalah nomor seri dari pabrik chip (8, 14, atau 20 karakter heksadesimal) dan tidak bisa diganti di kartu biasa. Karena itu tabel `kartu` memetakan UID ke NPM. NPM disimpan sebagai teks, bukan angka, supaya nol di depan tidak hilang dan tidak kena batas ukuran bilangan bulat.

## API

| Metode | Alamat | Fungsi |
|---|---|---|
| POST | `/tap` | Dipanggil ESP32: cek UID, catat absen, balas izin atau tolak |
| GET | `/kartu` | Daftar kartu |
| POST | `/kartu` | Daftarkan atau ubah kartu (`uid`, `nama`, `npm` opsional) |
| DELETE | `/kartu/{uid}` | Hapus kartu |
| GET | `/absen` | 50 riwayat terakhir |
| POST | `/absen` | Catat absen manual |
| GET | `/dashboard` | Halaman beranda |
| GET | `/dashboard/kartu` | Halaman kelola kartu |

Contoh:

```bash
curl -X POST localhost:8000/tap -H "Content-Type: application/json" -d '{"uid":"AABBCCDD"}'
```

## Struktur folder

```
absen-nfc-backend/
├── esp32/
│   └── absen_nfc.ino        # sketsa ESP32 (Wokwi)
├── server/
│   ├── main.py              # rute API dan dashboard
│   ├── db.py                # koneksi MySQL (pengaturan dari .env)
│   ├── skema.sql            # skema tabel, dibuat otomatis saat server mulai
│   ├── migrasi_sqlite.py    # pindah data lama dari SQLite ke MySQL
│   ├── requirements.txt
│   └── templates/           # halaman dashboard (Jinja2 + htmx)
├── mulai_db.sh              # menyalakan MariaDB
├── mulai_server.sh          # menyalakan database dan server
├── mulai_tunnel.sh          # membuka tunnel dan menampilkan alamatnya
└── .env.example             # contoh pengaturan database
```

## Menjalankan

Prasyarat: Python 3.12 dan MariaDB atau MySQL. Skrip `mulai_*.sh` ditulis untuk lingkungan Alpine (terminal Acode di Android). Di lingkungan lain, nyalakan database dengan cara biasa lalu jalankan servernya.

1. Ambil kode dan pasang kebutuhan:

```bash
git clone https://github.com/the1975/absen-nfc-backend.git
cd absen-nfc-backend
pip install -r server/requirements.txt
cp .env.example .env
```

2. Buat database dan pengguna, lalu isi sandinya di `.env`:

```sql
CREATE DATABASE absen_nfc CHARACTER SET utf8mb4;
CREATE USER 'absen'@'localhost' IDENTIFIED BY 'ganti_sandi';
GRANT ALL PRIVILEGES ON absen_nfc.* TO 'absen'@'localhost';
```

| Variabel `.env` | Isi |
|---|---|
| `DB_SOCKET` | Jalur soket MySQL (kalau diisi, dipakai dibanding host dan port) |
| `DB_HOST`, `DB_PORT` | Alamat database kalau tidak lewat soket |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Pengguna, sandi, dan nama database |

3. Nyalakan database dan server (tabel dibuat otomatis):

```bash
./mulai_server.sh
```

4. Buka `http://localhost:8000/dashboard`, lalu daftarkan kartu di halaman Kartu.
5. Untuk Wokwi: jalankan `./mulai_tunnel.sh`, salin alamat yang muncul ke `URL_DASAR` di sketsa, lalu jalankan simulasi dan tempelkan kartu.

## Tantangan dan solusi

| Masalah | Penyebab | Solusi |
|---|---|---|
| Dashboard selalu menulis "Belum ada tap" dan semua baris berkedip di awal | Rute `/dashboard` terdaftar dua kali, FastAPI memakai yang pertama (versi lama) | Versi lama dihapus, tinggal satu fungsi dan satu sumber data |
| Server error `Connection refused` setiap terminal baru dibuka | MariaDB dan server berjalan sebagai proses terminal, tidak menyala sendiri | Skrip `mulai_db.sh` dan `mulai_server.sh` yang memeriksa, menyalakan, dan menampilkan log kalau gagal |
| Ingin memakai NPM sebagai UID kartu | UID adalah nomor seri chip, tidak bisa diubah | Tabel pemetaan UID ke NPM, NPM disimpan sebagai teks |
| Alamat tunnel berganti-ganti | Domain gratis localhost.run dirotasi dan berubah tiap tunnel dibuka ulang | `mulai_tunnel.sh` menampilkan alamat terbaru, di perangkat asli diganti alamat IP lokal |
| Skrip tunnel menangkap alamat yang salah | Pola pencarian terlalu longgar sampai ikut mengambil nama di teks banner | Pola dipersempit hanya untuk alamat acak |
| Pindah dari SQLite ke MySQL | Beda sintaks (penanda parameter, upsert, tipe waktu) | Lapisan `db.py`, helper `kursor()`, dan skrip migrasi yang aman dijalankan ulang |

## Keterbatasan

- **Ini prototype.** Dashboard dan API belum memakai login. Siapa pun yang tahu alamat tunnel bisa membuka dashboard atau mengirim tap. Jangan dipakai untuk data nyata sebelum ada autentikasi.
- Mengenali orang hanya dari UID belum aman, karena UID pada sebagian kartu bisa disalin.
- Alamat tunnel gratis berganti, jadi `URL_DASAR` di Wokwi perlu diperbarui tiap sesi.
- Pintu masih berupa LED, belum perangkat sungguhan.

## Rencana berikutnya

- [ ] Login untuk dashboard
- [ ] ESP32 dan RC522 asli, memakai alamat IP lokal tanpa tunnel
- [ ] Kunci pintu sungguhan (relay atau solenoid)
- [ ] Sambung ke database MySQL kampus
- [ ] Ekspor riwayat (CSV) dan rekap per NPM

## Yang dipelajari di proyek ini

- Membangun REST API dengan FastAPI dan menyambungkannya ke MySQL (query berparameter, upsert, skema tabel)
- Membaca kartu RFID lewat SPI di ESP32 dan memanggil HTTP dari mikrokontroler
- Dashboard yang diperbarui otomatis dengan htmx tanpa menulis banyak JavaScript
- Migrasi data antar database dan merancang skrip yang aman dijalankan ulang
- Tunneling untuk menghubungkan simulator ke server lokal
- Alur Git yang rapi dengan awalan pesan commit `[ADD]`, `[EDIT]`, dan `[DEBUG]`

## Cara pengerjaan

Proyek ini dikerjakan bertahap dengan bantuan Claude (asisten AI dari Anthropic). Arah dan keputusannya dari saya: simulasi dulu sebelum alat asli, memakai MySQL, dan memetakan NPM ke tiap kartu. Claude membantu menjelaskan konsep dan menyusun draf kode per langkah. Setiap langkah saya jalankan sendiri di HP, saya uji, dan saya commit. Error yang muncul saya foto dan dibahas sampai ketemu penyebabnya, seperti yang tercatat di bagian Tantangan.

---

Dibuat oleh [@the1975](https://github.com/the1975)
