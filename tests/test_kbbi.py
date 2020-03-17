import pathlib

import pytest

DIR_KASUS = pathlib.Path(__file__).resolve(strict=True).parent / "kasus"

kasus = {
    j.name: [(p.stem, p) for p in (DIR_KASUS / j).iterdir() if p.is_file()]
    for j in DIR_KASUS.iterdir()
    if j.is_dir()
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
