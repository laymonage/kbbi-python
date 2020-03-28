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
def kbbi_mock(monkeypatch, request, autentikasi):
    if isinstance(request.param, (list, tuple)):
        _auth, lokasi = request.param
    else:
        _auth = request.param
        lokasi = None
    if _auth:
        _auth = autentikasi

    ___init__ = MockKBBI.__init__

    def __init__(self, kueri, auth=None):
        ___init__(self, kueri, auth=_auth, lokasi=lokasi)

    monkeypatch.setattr(MockKBBI, "__init__", __init__)
    monkeypatch.setattr(kbbi.kbbi, "KBBI", MockKBBI)


@pytest.fixture
def autentikasi_gagal(request, monkeypatch):
    monkeypatch.setattr(MockAutentikasiKBBI, "buat_galat", True)
    monkeypatch.setattr(kbbi.kbbi, "AutentikasiKBBI", MockAutentikasiKBBI)


@pytest.fixture
def autentikasi_sukses(request, monkeypatch):
    monkeypatch.setattr(MockAutentikasiKBBI, "paksa_sukses", True)
    monkeypatch.setattr(kbbi.kbbi, "AutentikasiKBBI", MockAutentikasiKBBI)


@pytest.fixture
def lokasi_kuki():
    return pathlib.Path("kukifix.json")


@pytest.fixture
def mock_lokasi_kuki(lokasi_kuki, monkeypatch):
    monkeypatch.setattr(kbbi.AutentikasiKBBI, "lokasi_kuki", lokasi_kuki)
    return lokasi_kuki


@pytest.fixture
def kuki(mock_lokasi_kuki):
    mock_lokasi_kuki.write_text('{".AspNet.ApplicationCookie": "kuki enak"}')
    return mock_lokasi_kuki


@pytest.fixture
def tanpa_kuki(lokasi_kuki):
    if lokasi_kuki.exists():
        lokasi_kuki.unlink()
    return lokasi_kuki
