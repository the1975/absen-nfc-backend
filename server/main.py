import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI
from pydantic import BaseModel

DB_FILE = "absen.db"
WIB = timezone(timedelta(hours=7))

app = FastAPI(title="Absen NFC Perpus")


class Absen(BaseModel):
    uid: str
    nama: str
    status: str


class KartuBaru(BaseModel):
    uid: str
    nama: str


class Tap(BaseModel):
    uid: str


def koneksi():
    return sqlite3.connect(DB_FILE)


def sekarang():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")


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
        db.execute(
            """CREATE TABLE IF NOT EXISTS kartu (
                uid TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                dibuat TEXT NOT NULL
            )"""
        )
        db.commit()


siapkan_db()


@app.get("/")
def beranda():
    return {"pesan": "Server absen NFC jalan"}


@app.post("/kartu")
def daftar_kartu(data: KartuBaru):
    uid = data.uid.strip().upper()
    nama = data.nama.strip()
    with closing(koneksi()) as db:
        db.execute(
            "INSERT INTO kartu (uid, nama, dibuat) VALUES (?, ?, ?) "
            "ON CONFLICT(uid) DO UPDATE SET nama = excluded.nama",
            (uid, nama, sekarang()),
        )
        db.commit()
    return {"ok": True, "uid": uid, "nama": nama}


@app.get("/kartu")
def daftar_semua_kartu():
    with closing(koneksi()) as db:
        db.row_factory = sqlite3.Row
        baris = db.execute("SELECT uid, nama, dibuat FROM kartu ORDER BY nama").fetchall()
    return [dict(b) for b in baris]


@app.delete("/kartu/{uid}")
def hapus_kartu(uid: str):
    with closing(koneksi()) as db:
        hasil = db.execute("DELETE FROM kartu WHERE uid = ?", (uid.strip().upper(),))
        db.commit()
    return {"ok": True, "dihapus": hasil.rowcount}


@app.post("/tap")
def tap_kartu(data: Tap):
    uid = data.uid.strip().upper()
    waktu = sekarang()
    with closing(koneksi()) as db:
        baris = db.execute("SELECT nama FROM kartu WHERE uid = ?", (uid,)).fetchone()
        izin = baris is not None
        nama = baris[0] if izin else "-"
        status = "diterima" if izin else "ditolak"
        db.execute(
            "INSERT INTO absen (uid, nama, status, waktu) VALUES (?, ?, ?, ?)",
            (uid, nama, status, waktu),
        )
        db.commit()
    print(f"[{waktu}] {nama} ({uid}) -> {status}")
    return {"izin": izin, "nama": nama, "waktu": waktu}


@app.post("/absen")
def terima_absen(data: Absen):
    waktu = sekarang()
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


from pathlib import Path
from fastapi.responses import HTMLResponse


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return (Path(__file__).parent / "dashboard.html").read_text(encoding="utf-8")
