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
def test_str_nonauth_dgn_eksp_nonauth(aktual_objek, ekspektasi_str):
    assert str(aktual_objek) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["str"],
    indirect=True,
    ids=idfn,
)
def test_str_auth_dgn_eksp_nonauth(
    aktual_objek_terautentikasi, ekspektasi_str
):
    assert (
        aktual_objek_terautentikasi.__str__(fitur_pengguna=False)
        == ekspektasi_str
    )


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["str-auth"],
    indirect=True,
    ids=idfn,
)
def test_str_auth_dgn_eksp_auth(aktual_objek_terautentikasi, ekspektasi_str):
    assert str(aktual_objek_terautentikasi) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_str",
    kasus["str_tanpa_contoh"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh_nonauth_dgn_eksp_nonauth(
    aktual_objek, ekspektasi_str
):
    assert aktual_objek.__str__(contoh=False) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["str_tanpa_contoh"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh_auth_dgn_eksp_nonauth(
    aktual_objek_terautentikasi, ekspektasi_str
):
    assert (
        aktual_objek_terautentikasi.__str__(contoh=False, fitur_pengguna=False)
        == ekspektasi_str
    )


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["str_tanpa_contoh-auth"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh_auth_dgn_eksp_auth(
    aktual_objek_terautentikasi, ekspektasi_str
):
    assert aktual_objek_terautentikasi.__str__(contoh=False) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_serialisasi",
    kasus["serialisasi"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi_nonauth_dgn_eksp_nonauth(
    aktual_objek, ekspektasi_serialisasi
):
    assert aktual_objek.serialisasi() == ekspektasi_serialisasi


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_serialisasi",
    kasus["serialisasi"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi_auth_dgn_eksp_nonauth(
    aktual_objek_terautentikasi, ekspektasi_serialisasi
):
    assert (
        aktual_objek_terautentikasi.serialisasi(fitur_pengguna=False)
        == ekspektasi_serialisasi
    )


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_serialisasi",
    kasus["serialisasi-auth"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi_auth_dgn_eksp_auth(
    aktual_objek_terautentikasi, ekspektasi_serialisasi
):
    assert aktual_objek_terautentikasi.serialisasi() == ekspektasi_serialisasi
