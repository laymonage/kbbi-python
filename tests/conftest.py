import json
import pathlib

import pytest

import kbbi
from _mock import MockAutentikasiKBBI, MockKBBI


@pytest.fixture
def autentikasi():
    return MockAutentikasiKBBI("foo", "bar")


@pytest.fixture(scope="session")
def laman():
    return dict()


@pytest.fixture(scope="session")
def laman_terautentikasi():
    return dict()


@pytest.fixture
def ekspektasi_str(request):
    path = request.param
    with path.open("r") as berkas:
        yield berkas.read().strip()


@pytest.fixture
def ekspektasi_serialisasi(request):
    path = request.param
    with path.open("r") as berkas:
        return json.load(berkas)


def ambil_atau_simpan(dct, key, func):
    try:
        return dct[key]
    except KeyError:
        dct[key] = func(key)
        return dct[key]


@pytest.fixture
def aktual_objek(request, laman):
    kueri = request.param
    return ambil_atau_simpan(laman, kueri, lambda a: MockKBBI(a))


@pytest.fixture
def aktual_objek_terautentikasi(request, autentikasi, laman_terautentikasi):
    kueri = request.param
    return ambil_atau_simpan(
        laman_terautentikasi, kueri, lambda a: MockKBBI(a, autentikasi)
    )


@pytest.fixture
def lokasi(request):
    tujuan = request.param.split("/")
    hasil = pathlib.Path(__file__).parent
    for direktori in tujuan:
        hasil /= direktori
    return hasil


@pytest.fixture
def kbbi_mock(monkeypatch, request):
    if isinstance(request.param, (list, tuple)):
        auth, lokasi = request.param
    else:
        auth = request.param
        lokasi = None
    _host = kbbi.KBBI.host
    __init_lokasi = kbbi.KBBI._init_lokasi
    __init_entri = kbbi.KBBI._init_entri

    def _init_lokasi(self):
        if lokasi is None:
            __init_lokasi(self)
            self.lokasi = f"{auth}/{self.lokasi}.html".replace("?frasa=", "/")
        else:
            self.lokasi = lokasi

    def _init_entri(self, laman):
        __init_entri(self, laman)
        __init_lokasi(self)
        self.host = _host

    monkeypatch.setattr(kbbi.KBBI, "host", "http://localhost:8000")
    monkeypatch.setattr(kbbi.KBBI, "_init_lokasi", _init_lokasi)
    monkeypatch.setattr(kbbi.KBBI, "_init_entri", _init_entri)


@pytest.fixture
def lokasi_kuki(monkeypatch):
    lokasi = pathlib.Path("kukifix.json")
    monkeypatch.setattr(kbbi.AutentikasiKBBI, "lokasi_kuki", lokasi)
    return lokasi


@pytest.fixture
def kuki(lokasi_kuki):
    lokasi_kuki.write_text('{".AspNet.ApplicationCookie": "kuki enak"}')
    return lokasi_kuki


@pytest.fixture
def tanpa_kuki(lokasi_kuki):
    if lokasi_kuki.exists():
        lokasi_kuki.unlink()
    return lokasi_kuki
