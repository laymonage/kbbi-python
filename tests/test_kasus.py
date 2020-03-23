import pathlib

import pytest

DIR_KASUS = pathlib.Path(__file__).resolve(strict=True).parent / "kasus"

kasus = {"auth": {}, "nonauth": {}}

for k in kasus:
    for jenis in (DIR_KASUS / k).iterdir():
        if jenis.is_dir():
            kasus[k][jenis.stem] = [
                (f.stem, f) for f in jenis.iterdir() if f.is_file()
            ]


def idfn(val):
    if isinstance(val, pathlib.Path):
        return val.name
    return val


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_str",
    kasus["nonauth"]["str"],
    indirect=True,
    ids=idfn,
)
def test_str_nonauth_dgn_eksp_nonauth(aktual_objek, ekspektasi_str):
    assert str(aktual_objek) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["nonauth"]["str"],
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
    kasus["auth"]["str"],
    indirect=True,
    ids=idfn,
)
def test_str_auth_dgn_eksp_auth(aktual_objek_terautentikasi, ekspektasi_str):
    assert str(aktual_objek_terautentikasi) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_str",
    kasus["nonauth"]["str_tanpa_contoh"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh_nonauth_dgn_eksp_nonauth(
    aktual_objek, ekspektasi_str
):
    assert aktual_objek.__str__(contoh=False) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_str",
    kasus["nonauth"]["str_tanpa_contoh"],
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
    kasus["auth"]["str_tanpa_contoh"],
    indirect=True,
    ids=idfn,
)
def test_str_tanpa_contoh_auth_dgn_eksp_auth(
    aktual_objek_terautentikasi, ekspektasi_str
):
    assert aktual_objek_terautentikasi.__str__(contoh=False) == ekspektasi_str


@pytest.mark.parametrize(
    "aktual_objek,ekspektasi_serialisasi",
    kasus["nonauth"]["serialisasi"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi_nonauth_dgn_eksp_nonauth(
    aktual_objek, ekspektasi_serialisasi
):
    assert aktual_objek.serialisasi() == ekspektasi_serialisasi


@pytest.mark.parametrize(
    "aktual_objek_terautentikasi,ekspektasi_serialisasi",
    kasus["nonauth"]["serialisasi"],
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
    kasus["auth"]["serialisasi"],
    indirect=True,
    ids=idfn,
)
def test_serialisasi_auth_dgn_eksp_auth(
    aktual_objek_terautentikasi, ekspektasi_serialisasi
):
    assert aktual_objek_terautentikasi.serialisasi() == ekspektasi_serialisasi
