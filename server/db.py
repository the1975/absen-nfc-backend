import os
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor


def _muat_env():
    berkas = Path(__file__).resolve().parent.parent / ".env"
    if not berkas.exists():
        return
    for baris in berkas.read_text().splitlines():
        baris = baris.strip()
        if baris and not baris.startswith("#") and "=" in baris:
            kunci, nilai = baris.split("=", 1)
            os.environ.setdefault(kunci.strip(), nilai.strip())


_muat_env()


def koneksi():
    pengaturan = dict(
        user=os.getenv("DB_USER", "absen"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "absen_nfc"),
        charset="utf8mb4",
        cursorclass=DictCursor,
    )
    soket = os.getenv("DB_SOCKET")
    if soket:
        pengaturan["unix_socket"] = soket
    else:
        pengaturan["host"] = os.getenv("DB_HOST", "localhost")
        pengaturan["port"] = int(os.getenv("DB_PORT", "3306"))
    return pymysql.connect(**pengaturan)
