import pathlib

import pytest

BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent

jenis = ["serialisasi", "str", "str_tanpa_contoh"]
kasus = {
    j: [(p.stem, p) for p in (BASE_DIR / "kasus" / j).iterdir() if p.is_file()]
    for j in jenis
}


def idfn(val):
    if isinstance(val, pathlib.Path):
        return val.name
    return val


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_str", kasus["str"], indirect=True, ids=idfn
)
def test_str(aktual_objek, ekspektasi_str):
    assert str(aktual_objek) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_str",
    kasus["str_tanpa_contoh"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh(aktual_objek, ekspektasi_str):
    assert aktual_objek.__str__(contoh=False) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_serialisasi",
    kasus["serialisasi"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi(aktual_objek, ekspektasi_serialisasi):
    assert aktual_objek.serialisasi() == ekspektasi_serialisasi
