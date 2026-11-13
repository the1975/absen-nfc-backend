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
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def tanggal_indo():
    n = datetime.now(WIB)
    return f"{HARI[n.weekday()]}, {n.day} {BULAN[n.month - 1]}"


def waktu_relatif(teks):
    try:
        t = datetime.strptime(teks, "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB)
    except ValueError:
        return teks
    selisih = int((datetime.now(WIB) - t).total_seconds())
    if selisih < 60:
        return "baru saja"
    if selisih < 3600:
        return f"{selisih // 60} menit lalu"
    if selisih < 86400:
        return f"{selisih // 3600} jam lalu"
    return t.strftime("%d/%m/%Y")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    hari_ini = sekarang()[:10] + "%"
    with closing(koneksi()) as db:
        db.row_factory = sqlite3.Row
        absen = [dict(b) for b in db.execute(
            "SELECT uid, nama, status, waktu FROM absen ORDER BY id DESC LIMIT 20")]
        diterima = db.execute(
            "SELECT COUNT(*) FROM absen WHERE status = 'diterima' AND waktu LIKE ?", (hari_ini,)).fetchone()[0]
        ditolak = db.execute(
            "SELECT COUNT(*) FROM absen WHERE status != 'diterima' AND waktu LIKE ?", (hari_ini,)).fetchone()[0]
        jumlah_kartu = db.execute("SELECT COUNT(*) FROM kartu").fetchone()[0]
    for a in absen:
        a["jam"] = a["waktu"][11:16]
        a["relatif"] = waktu_relatif(a["waktu"])
    terakhir = waktu_relatif(absen[0]["waktu"]) if absen else None
    return templates.TemplateResponse(
        request=request, name="beranda.html",
        context={"absen": absen, "diterima": diterima, "ditolak": ditolak,
                 "jumlah_kartu": jumlah_kartu, "tanggal": tanggal_indo(), "terakhir": terakhir})
def ambil_data(terakhir_id=None, status="semua"):
    hari_ini = sekarang()[:10] + "%"
    kondisi = {"diterima": "WHERE status = 'diterima'",
               "ditolak": "WHERE status != 'diterima'"}.get(status, "")
    with closing(koneksi()) as db:
        db.row_factory = sqlite3.Row
        absen = [dict(b) for b in db.execute(
            f"SELECT id, uid, nama, status, waktu FROM absen {kondisi} ORDER BY id DESC LIMIT 20")]
        diterima = db.execute(
            "SELECT COUNT(*) FROM absen WHERE status = 'diterima' AND waktu LIKE ?", (hari_ini,)).fetchone()[0]
        ditolak = db.execute(
            "SELECT COUNT(*) FROM absen WHERE status != 'diterima' AND waktu LIKE ?", (hari_ini,)).fetchone()[0]
        jumlah_kartu = db.execute("SELECT COUNT(*) FROM kartu").fetchone()[0]
        terbaru = db.execute("SELECT id, waktu FROM absen ORDER BY id DESC LIMIT 1").fetchone()
    for a in absen:
        a["jam"] = a["waktu"][11:16]
        a["baru"] = terakhir_id is not None and a["id"] > terakhir_id
    return {
        "absen": absen, "diterima": diterima, "ditolak": ditolak, "jumlah_kartu": jumlah_kartu,
        "status": status,
        "tanggal": tanggal_indo(),
        "id_terbaru": terbaru["id"] if terbaru else 0,
        "tap_terakhir": waktu_relatif(terbaru["waktu"]) if terbaru else None,
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    data = ambil_data()
    data["awal"] = True
    data["tanggal"] = tanggal_indo()
    return templates.TemplateResponse(request=request, name="beranda.html", context=data)


@app.get("/dashboard/bagian", response_class=HTMLResponse)
def dashboard_bagian(request: Request, terakhir: int = 0, status: str = "semua"):
    if status not in ("semua", "diterima", "ditolak"):
        status = "semua"
    return templates.TemplateResponse(
        request=request, name="_ringkasan.html", context=ambil_data(terakhir, status))


import re
from html import escape
from fastapi import Form


def semua_kartu():
    with closing(koneksi()) as db:
        db.row_factory = sqlite3.Row
        return [dict(b) for b in db.execute(
            "SELECT uid, nama FROM kartu ORDER BY nama COLLATE NOCASE")]


@app.get("/dashboard/kartu", response_class=HTMLResponse)
def halaman_kartu(request: Request):
    return templates.TemplateResponse(
        request=request, name="kartu.html", context={"kartu": semua_kartu(), "aktif": "kartu"})


@app.post("/dashboard/kartu", response_class=HTMLResponse)
def tambah_kartu_web(request: Request, uid: str = Form(""), nama: str = Form("")):
    uid = re.sub(r"[\s:\-]", "", uid).upper()
    nama = " ".join(nama.split())
    galat = None
    if not re.fullmatch(r"[0-9A-F]{8}|[0-9A-F]{14}|[0-9A-F]{20}", uid):
        galat = "UID harus 8, 14, atau 20 karakter berupa angka dan huruf A-F. Contoh: AABBCCDD"
    elif not nama or len(nama) > 40:
        galat = "Nama wajib diisi, maksimal 40 karakter."
    if galat:
        return HTMLResponse(escape(galat), headers={"HX-Retarget": "#pesan-form", "HX-Reswap": "innerHTML"})
    with closing(koneksi()) as db:
        db.execute(
            "INSERT INTO kartu (uid, nama, dibuat) VALUES (?, ?, ?) "
            "ON CONFLICT(uid) DO UPDATE SET nama = excluded.nama",
            (uid, nama, sekarang()),
        )
        db.commit()
    return templates.TemplateResponse(
        request=request, name="_daftar_kartu.html", context={"kartu": semua_kartu()},
        headers={"HX-Trigger": "kartu-tersimpan"})


@app.delete("/dashboard/kartu/{uid}", response_class=HTMLResponse)
def hapus_kartu_web(request: Request, uid: str):
    with closing(koneksi()) as db:
        db.execute("DELETE FROM kartu WHERE uid = ?", (uid.strip().upper(),))
        db.commit()
    return templates.TemplateResponse(
        request=request, name="_daftar_kartu.html", context={"kartu": semua_kartu()})
