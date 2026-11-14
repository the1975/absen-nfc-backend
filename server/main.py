import os
import re
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader, HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from db import koneksi

# Pengaturan keamanan dibaca dari .env (db.py sudah memuatnya)
API_KEY = os.getenv("API_KEY", "")
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")

kunci_header = APIKeyHeader(name="X-API-Key", auto_error=False)
login_basic = HTTPBasic(auto_error=False)


def sama(a, b):
    # Perbandingan teks yang tahan serangan waktu
    return secrets.compare_digest(a.encode(), b.encode())


def wajib_kunci(kunci: str = Depends(kunci_header)):
    # Untuk perangkat (ESP32): kunci dikirim lewat header X-API-Key
    if not API_KEY:
        raise HTTPException(status_code=503, detail="API_KEY belum diatur di .env")
    if not kunci or not sama(kunci, API_KEY):
        raise HTTPException(status_code=401, detail="Kunci API salah atau tidak ada")


def wajib_login(kredensial: HTTPBasicCredentials = Depends(login_basic)):
    # Untuk dashboard dan data: browser menampilkan kotak login
    if not DASHBOARD_USER or not DASHBOARD_PASSWORD:
        raise HTTPException(status_code=503,
                            detail="DASHBOARD_USER dan DASHBOARD_PASSWORD belum diatur di .env")
    pengguna_ok = kredensial is not None and sama(kredensial.username, DASHBOARD_USER)
    sandi_ok = kredensial is not None and sama(kredensial.password, DASHBOARD_PASSWORD)
    if not (pengguna_ok and sandi_ok):
        raise HTTPException(status_code=401, detail="Login diperlukan",
                            headers={"WWW-Authenticate": 'Basic realm="Absen NFC"'})

WIB = timezone(timedelta(hours=7))
FORMAT_WAKTU = "%Y-%m-%d %H:%M:%S"

app = FastAPI(title="Absen NFC Perpus")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


class Absen(BaseModel):
    uid: str
    nama: str
    status: str


class KartuBaru(BaseModel):
    uid: str
    nama: str
    npm: str = ""


class Tap(BaseModel):
    uid: str


def sekarang():
    return datetime.now(WIB).strftime(FORMAT_WAKTU)


@contextmanager
def kursor():
    # Satu koneksi per permintaan: commit kalau sukses, selalu ditutup
    db = koneksi()
    try:
        with db.cursor() as cur:
            yield cur
        db.commit()
    finally:
        db.close()


def rapikan(baris):
    # Kolom DATETIME dijadikan teks, sama seperti waktu di SQLite dulu
    return {k: (v.strftime(FORMAT_WAKTU) if isinstance(v, datetime) else v)
            for k, v in baris.items()}


PANJANG_NPM = 10


def bersihkan_npm(npm):
    # NPM boleh kosong; kalau diisi harus angka saja sepanjang PANJANG_NPM
    npm = "".join((npm or "").split())
    if npm and not (npm.isascii() and npm.isdigit() and len(npm) == PANJANG_NPM):
        return None, f"NPM harus {PANJANG_NPM} angka."
    return (npm or None), None


def siapkan_db():
    skema = (Path(__file__).parent / "skema.sql").read_text()
    with kursor() as cur:
        for pernyataan in skema.split(";"):
            if pernyataan.strip():
                cur.execute(pernyataan)


siapkan_db()


@app.get("/")
def beranda():
    return {"pesan": "Server absen NFC jalan"}


@app.post("/kartu", dependencies=[Depends(wajib_login)])
def daftar_kartu(data: KartuBaru):
    uid = data.uid.strip().upper()
    nama = data.nama.strip()
    npm, galat = bersihkan_npm(data.npm)
    if galat:
        raise HTTPException(status_code=422, detail=galat)
    with kursor() as cur:
        cur.execute(
            "INSERT INTO kartu (uid, npm, nama, dibuat) VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE npm = VALUES(npm), nama = VALUES(nama)",
            (uid, npm, nama, sekarang()),
        )
    return {"ok": True, "uid": uid, "npm": npm, "nama": nama}


@app.get("/kartu", dependencies=[Depends(wajib_login)])
def daftar_semua_kartu():
    with kursor() as cur:
        cur.execute("SELECT uid, npm, nama, dibuat FROM kartu ORDER BY nama")
        return [rapikan(b) for b in cur.fetchall()]


@app.delete("/kartu/{uid}", dependencies=[Depends(wajib_login)])
def hapus_kartu(uid: str):
    with kursor() as cur:
        dihapus = cur.execute("DELETE FROM kartu WHERE uid = %s", (uid.strip().upper(),))
    return {"ok": True, "dihapus": dihapus}


@app.post("/tap", dependencies=[Depends(wajib_kunci)])
def tap_kartu(data: Tap):
    uid = data.uid.strip().upper()
    waktu = sekarang()
    with kursor() as cur:
        cur.execute("SELECT nama, npm FROM kartu WHERE uid = %s", (uid,))
        baris = cur.fetchone()
        izin = baris is not None
        nama = baris["nama"] if izin else "-"
        npm = baris["npm"] if izin else None
        status = "diterima" if izin else "ditolak"
        cur.execute(
            "INSERT INTO absen (uid, npm, nama, status, waktu) VALUES (%s, %s, %s, %s, %s)",
            (uid, npm, nama, status, waktu),
        )
    print(f"[{waktu}] {nama} ({uid}) -> {status}")
    return {"izin": izin, "nama": nama, "npm": npm, "waktu": waktu}


@app.post("/absen", dependencies=[Depends(wajib_kunci)])
def terima_absen(data: Absen):
    waktu = sekarang()
    with kursor() as cur:
        cur.execute(
            "INSERT INTO absen (uid, nama, status, waktu) VALUES (%s, %s, %s, %s)",
            (data.uid, data.nama, data.status, waktu),
        )
    print(f"[{waktu}] {data.nama} ({data.uid}) -> {data.status}")
    return {"ok": True, "waktu": waktu}


@app.get("/absen", dependencies=[Depends(wajib_login)])
def daftar_absen():
    with kursor() as cur:
        cur.execute("SELECT id, uid, npm, nama, status, waktu FROM absen ORDER BY id DESC LIMIT 50")
        return [rapikan(b) for b in cur.fetchall()]


HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def tanggal_indo():
    n = datetime.now(WIB)
    return f"{HARI[n.weekday()]}, {n.day} {BULAN[n.month - 1]}"


def waktu_relatif(teks):
    try:
        t = datetime.strptime(teks, FORMAT_WAKTU).replace(tzinfo=WIB)
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


def ambil_data(terakhir_id=None, status="semua"):
    awal_hari = sekarang()[:10] + " 00:00:00"
    kondisi = {"diterima": "WHERE status = 'diterima'",
               "ditolak": "WHERE status != 'diterima'"}.get(status, "")
    with kursor() as cur:
        cur.execute(
            f"SELECT id, uid, npm, nama, status, waktu FROM absen {kondisi} ORDER BY id DESC LIMIT 20")
        absen = [rapikan(b) for b in cur.fetchall()]
        cur.execute(
            "SELECT COUNT(*) AS n FROM absen WHERE status = 'diterima' AND waktu >= %s", (awal_hari,))
        diterima = cur.fetchone()["n"]
        cur.execute(
            "SELECT COUNT(*) AS n FROM absen WHERE status != 'diterima' AND waktu >= %s", (awal_hari,))
        ditolak = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM kartu")
        jumlah_kartu = cur.fetchone()["n"]
        cur.execute("SELECT id, waktu FROM absen ORDER BY id DESC LIMIT 1")
        terbaru = cur.fetchone()
    terbaru = rapikan(terbaru) if terbaru else None
    for a in absen:
        a["jam"] = a["waktu"][11:16]
        a["relatif"] = waktu_relatif(a["waktu"])
        a["baru"] = terakhir_id is not None and a["id"] > terakhir_id
    return {
        "absen": absen, "diterima": diterima, "ditolak": ditolak, "jumlah_kartu": jumlah_kartu,
        "status": status,
        "tanggal": tanggal_indo(),
        "id_terbaru": terbaru["id"] if terbaru else 0,
        "tap_terakhir": waktu_relatif(terbaru["waktu"]) if terbaru else None,
    }


@app.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(wajib_login)])
def dashboard(request: Request):
    data = ambil_data()
    data["awal"] = True
    return templates.TemplateResponse(request=request, name="beranda.html", context=data)


@app.get("/dashboard/bagian", response_class=HTMLResponse, dependencies=[Depends(wajib_login)])
def dashboard_bagian(request: Request, terakhir: int = 0, status: str = "semua"):
    if status not in ("semua", "diterima", "ditolak"):
        status = "semua"
    return templates.TemplateResponse(
        request=request, name="_ringkasan.html", context=ambil_data(terakhir, status))


def semua_kartu():
    with kursor() as cur:
        cur.execute("SELECT uid, npm, nama FROM kartu ORDER BY nama")
        return cur.fetchall()


@app.get("/dashboard/kartu", response_class=HTMLResponse, dependencies=[Depends(wajib_login)])
def halaman_kartu(request: Request):
    return templates.TemplateResponse(
        request=request, name="kartu.html", context={"kartu": semua_kartu(), "aktif": "kartu"})


@app.post("/dashboard/kartu", response_class=HTMLResponse, dependencies=[Depends(wajib_login)])
def tambah_kartu_web(request: Request, uid: str = Form(""), nama: str = Form(""), npm: str = Form("")):
    uid = re.sub(r"[\s:\-]", "", uid).upper()
    nama = " ".join(nama.split())
    galat = None
    if not re.fullmatch(r"[0-9A-F]{8}|[0-9A-F]{14}|[0-9A-F]{20}", uid):
        galat = "UID harus 8, 14, atau 20 karakter berupa angka dan huruf A-F. Contoh: AABBCCDD"
    elif not nama or len(nama) > 40:
        galat = "Nama wajib diisi, maksimal 40 karakter."
    else:
        npm, galat = bersihkan_npm(npm)
    if galat:
        return HTMLResponse(escape(galat), headers={"HX-Retarget": "#pesan-form", "HX-Reswap": "innerHTML"})
    with kursor() as cur:
        cur.execute(
            "INSERT INTO kartu (uid, npm, nama, dibuat) VALUES (%s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE npm = VALUES(npm), nama = VALUES(nama)",
            (uid, npm, nama, sekarang()),
        )
    return templates.TemplateResponse(
        request=request, name="_daftar_kartu.html", context={"kartu": semua_kartu()},
        headers={"HX-Trigger": "kartu-tersimpan"})


@app.delete("/dashboard/kartu/{uid}", response_class=HTMLResponse, dependencies=[Depends(wajib_login)])
def hapus_kartu_web(request: Request, uid: str):
    with kursor() as cur:
        cur.execute("DELETE FROM kartu WHERE uid = %s", (uid.strip().upper(),))
    return templates.TemplateResponse(
        request=request, name="_daftar_kartu.html", context={"kartu": semua_kartu()})
