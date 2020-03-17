import json

import pytest

from kbbi import KBBI


@pytest.fixture(scope="session")
def laman():
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


@pytest.fixture
def aktual_objek(request, laman):
    kueri = request.param
    try:
        return laman[kueri]
    except KeyError:
        laman[kueri] = KBBI(kueri)
        return laman[kueri]
