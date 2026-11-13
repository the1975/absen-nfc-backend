import sqlite3
import sys
from pathlib import Path

from db import koneksi

AKAR = Path(__file__).resolve().parent
kandidat = [AKAR / "absen.db", AKAR.parent / "absen.db", Path.cwd() / "absen.db"]
sumber = next((p for p in kandidat if p.exists()), None)
if sumber is None:
    print("absen.db tidak ditemukan")
    sys.exit(1)
print("Sumber SQLite:", sumber)

lama = sqlite3.connect(sumber)
lama.row_factory = sqlite3.Row
kartu = lama.execute("SELECT uid, nama, dibuat FROM kartu").fetchall()
absen = lama.execute("SELECT uid, nama, status, waktu FROM absen ORDER BY id").fetchall()

db = koneksi()
cur = db.cursor()

for k in kartu:
    cur.execute(
        "INSERT INTO kartu (uid, nama, dibuat) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE nama = VALUES(nama)",
        (k["uid"], k["nama"], k["dibuat"]),
    )
print("Kartu dipindah:", len(kartu))

cur.execute("SELECT COUNT(*) AS n FROM absen")
if cur.fetchone()["n"] == 0:
    cur.executemany(
        "INSERT INTO absen (uid, nama, status, waktu) VALUES (%s, %s, %s, %s)",
        [(a["uid"], a["nama"], a["status"], a["waktu"]) for a in absen],
    )
    print("Riwayat absen dipindah:", len(absen))
else:
    print("Tabel absen MySQL sudah berisi, riwayat dilewati")

db.commit()
db.close()
