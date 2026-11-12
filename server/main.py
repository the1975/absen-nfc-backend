import sqlite3
from contextlib import closing
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

DB_FILE = "absen.db"

app = FastAPI(title="Absen NFC Perpus")


class Absen(BaseModel):
    uid: str
    nama: str
    status: str


def koneksi():
    return sqlite3.connect(DB_FILE)


def siapkan_db():
    with closing(koneksi()) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS absen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT NOT NULL,
                nama TEXT NOT NULL,
                status TEXT NOT NULL,
                waktu TEXT NOT NULL
            )"""
        )
        db.commit()


siapkan_db()


@app.get("/")
def beranda():
    return {"pesan": "Server absen NFC jalan"}


@app.post("/absen")
def terima_absen(data: Absen):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with closing(koneksi()) as db:
        db.execute(
            "INSERT INTO absen (uid, nama, status, waktu) VALUES (?, ?, ?, ?)",
            (data.uid, data.nama, data.status, waktu),
        )
        db.commit()
    print(f"[{waktu}] {data.nama} ({data.uid}) -> {data.status}")
    return {"ok": True, "waktu": waktu}


@app.get("/absen")
def daftar_absen():
    with closing(koneksi()) as db:
        db.row_factory = sqlite3.Row
        baris = db.execute(
            "SELECT id, uid, nama, status, waktu FROM absen ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return [dict(b) for b in baris]
