import json
import os

import pytest

from kbbi import KBBI, AutentikasiKBBI


@pytest.fixture(scope="session")
def autentikasi():
    return AutentikasiKBBI(os.getenv("KBBI_POSEL"), os.getenv("KBBI_SANDI"))


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
    return ambil_atau_simpan(laman, kueri, lambda a: KBBI(a))


@pytest.fixture
def aktual_objek_terautentikasi(request, autentikasi, laman_terautentikasi):
    kueri = request.param
    return ambil_atau_simpan(
        laman_terautentikasi, kueri, lambda a: KBBI(a, autentikasi)
    )
