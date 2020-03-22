#!/usr/bin/env python
import json
import os
import pathlib
import sys

import requests

from _mock import MockAutentikasiKBBI, MockKBBI
from kbbi import KBBI, AutentikasiKBBI

DIR_INI = pathlib.Path(__file__).resolve(strict=True).parent
DIR_KASUS = DIR_INI / "kasus"

laman = [
    "a.n.",  # entri mengandung titik
    "air",  # bentuk tidak baku mengandung nomor
    "alam",  # ada 3 entri, 2 etimologi, entri kedua berupa prakategorial
    "asalamualaikum",  # etimologi tanpa kelas
    "beruang",  # ada makna dengan kelas kata kiasan (hijau)
    "bin",  # kasus khusus
    "civitas academica",  # judul entri bercetak miring
    "karbon dioksida",  # terdapat info (rumus kimia)
    "khayal",  # makna pernah gagal diproses
    "keratabasa",  # terdapat string bercetak miring pada salah satu submakna
    "kan",  # banyak entri singkat, bercampur dengan imbuhan
    "lah",  # jika terautentikasi terdapat kelas dan makna berupa pranala
    "lampir",  # satu entri prakategorial
    "makin",  # terdapat bentuk tidak baku
    "me-",  # terdapat entri berupa "lihat", terdapat varian
    "menjadikan",  # contoh dengan ~ (bukan --) untuk menggantikan entri
    "quo vadis?",  # terdapat ? dan judul entri bercetak miring
    "ranah",  # terdapat contoh berwarna cokelat
    "roh",  # contoh sederhana untuk etimologi, terdapat kiasan
    "sage",  # terdapat info (bahasa latin)
    "semakin",  # terdapat entri tanpa makna dan entri lain berupa rujukan
    "tampak",  # terdapat rujukan dengan nomor
]


def _buat(semua, func, direktori, ekstensi):
    for auth, objs in semua.items():
        path = DIR_KASUS / auth / direktori
        path.mkdir(parents=True, exist_ok=True)
        for obj in objs:
            berkas = path / f"{obj.nama}.{ekstensi}"
            berkas.write_text(f"{func(obj)}\n")


def buat_str(semua, direktori="str", **kwargs):
    _buat(semua, lambda obj: obj.__str__(**kwargs), direktori, "txt")


def buat_str_tanpa_contoh(semua):
    buat_str(semua, "str_tanpa_contoh", contoh=False)


def buat_serialisasi(semua):
    _buat(
        semua,
        lambda obj: json.dumps(obj.serialisasi(), indent=2),
        "serialisasi",
        "json",
    )


jenis = [buat_str, buat_str_tanpa_contoh, buat_serialisasi]


class PengunduhKBBI:
    root = DIR_INI
    host = KBBI.host
    _init_lokasi = KBBI._init_lokasi

    def __init__(self, nama, sesi=None, direktori="html"):
        self.nama = nama
        self.auth = bool(sesi)
        self.sesi = sesi or requests.Session()
        self.root /= direktori
        self._init_lokasi()
        self._path()

    @classmethod
    def _unduh(cls, klien, lokasi, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(klien.get(f"{cls.host}/{lokasi}").content)

    @classmethod
    def unduh_laman(cls, laman=None, sesi=None, direktori="html"):
        path = laman.split("/")
        tujuan = cls.root / direktori
        for p in path[:-1]:
            tujuan /= p
        tujuan /= f"{path[-1]}.html"
        cls._unduh(sesi or requests, laman, tujuan)

    @classmethod
    def unduh_laman_umum(cls, sesi=None, direktori="html"):
        for laman in {"Account/Login", "Beranda/Error", "Beranda/BatasSehari"}:
            cls.unduh_laman(laman, sesi, direktori)

    def _path(self):
        direktori = self.root / ("auth" if self.auth else "nonauth")
        if self.lokasi.startswith("entri/"):
            direktori = direktori / "entri"
        else:
            direktori = direktori / "Cari" / "Hasil"
        self.path = direktori / f"{self.nama}.html"

    def unduh(self):
        self._unduh(self.sesi, self.lokasi, self.path)


def unduh_html(daftar):
    auth = AutentikasiKBBI(os.getenv("KBBI_POSEL"), os.getenv("KBBI_SANDI"))
    total = len(daftar)
    for i, laman in enumerate(daftar, 1):
        print(f'({i}/{total}) Mengambil "{laman}"...')
        PengunduhKBBI(laman).unduh()
        PengunduhKBBI(laman, auth.sesi).unduh()


def buat_semua_objek(daftar):
    auth = MockAutentikasiKBBI("foo", "bar")
    semua = {"auth": [], "nonauth": []}
    for l in daftar:
        semua["auth"].append(MockKBBI(l, auth))
        semua["nonauth"].append(MockKBBI(l))
    return semua


def buat_semua_kasus(semua, jenis):
    for laman, objek in semua.items():
        for buat in jenis:
            buat(semua)


def main(daftar=None):
    if not daftar:
        daftar = laman
    unduh_html(daftar)
    semua = buat_semua_objek(daftar)
    buat_semua_kasus(semua, jenis)
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--init"]:
        PengunduhKBBI.unduh_laman_umum()
        sys.exit(0)
    try:
        sys.exit(main(args))
    except KeyboardInterrupt:
        print("\nKeluar...")
