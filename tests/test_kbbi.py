import json
import pathlib

import pytest

import kbbi


def test_objek_auth_kelas_lain():
    with pytest.raises(ValueError) as e:
        kbbi.KBBI("halo", True)
    assert str(e.value) == "'auth' harus berupa objek AutentikasiKBBI."


@pytest.mark.parametrize("aktual_objek", ["alam"], indirect=True)
def test_repr_kbbi(aktual_objek):
    assert repr(aktual_objek) == "<KBBI: alam>"


@pytest.mark.parametrize("aktual_objek", ["alam"], indirect=True)
def test_repr_entri(aktual_objek):
    assert repr(aktual_objek.entri[0]) == "<Entri: alam (1)>"


@pytest.mark.parametrize("aktual_objek", ["a.n."], indirect=True)
def test_repr_makna(aktual_objek):
    assert repr(aktual_objek.entri[0].makna[0]) == "<Makna: atas nama>"


@pytest.mark.parametrize("aktual_objek_terautentikasi", ["roh"], indirect=True)
def test_repr_etimologi(aktual_objek_terautentikasi):
    assert (
        repr(aktual_objek_terautentikasi.entri[0].etimologi)
        == "<Etimologi: رُوْحٌ>"
    )


def test_autentikasi_tanpa_posel_sandi_kuki_tidak_ada():
    with pytest.raises(kbbi.GagalAutentikasi) as e:
        kbbi.AutentikasiKBBI(lokasi_kuki="/lokasi/tidak/ada")
    assert str(e.value) == (
        "Posel dan sandi tidak diberikan, "
        "tetapi kuki tidak ditemukan di /lokasi/tidak/ada"
    )


def test_simpan_kuki(autentikasi):
    autentikasi.sesi.cookies.set(".AspNet.ApplicationCookie", "delicious")
    berkas = pathlib.Path("kukiku.json")
    assert not berkas.exists()
    autentikasi.lokasi_kuki = berkas
    autentikasi.simpan_kuki()
    with berkas.open() as kuki:
        assert json.load(kuki) == {".AspNet.ApplicationCookie": "delicious"}
    berkas.unlink()


def test_ambil_kuki(autentikasi):
    berkas = pathlib.Path("kukimu.json")
    with berkas.open("w") as kuki:
        json.dump({".AspNet.ApplicationCookie": "yummy"}, kuki)
    assert autentikasi.sesi.cookies.get(".AspNet.ApplicationCookie") is None
    autentikasi.lokasi_kuki = berkas
    autentikasi.ambil_kuki()
    assert autentikasi.sesi.cookies.get(".AspNet.ApplicationCookie") == "yummy"
    berkas.unlink()


def test_autentikasi_tidak_ada_token(autentikasi):
    autentikasi.lokasi = "Beranda/Error.html"
    with pytest.raises(kbbi.TerjadiKesalahan) as e:
        autentikasi._ambil_token()
    assert str(e.value) == "Terjadi kesalahan saat memproses permintaan Anda."


def test_autentikasi_gagal_tetap_halaman_login(autentikasi):
    with pytest.raises(kbbi.GagalAutentikasi) as e:
        autentikasi._autentikasi("pos@l.sy", "salah", "token", buat_galat=True)
    assert str(e.value) == (
        "Gagal melakukan autentikasi dengan alamat posel dan sandi "
        "yang diberikan."
    )


def test_autentikasi_gagal_laman_galat(autentikasi):
    autentikasi.lokasi = "Beranda/Error.html"
    with pytest.raises(kbbi.TerjadiKesalahan) as e:
        autentikasi._autentikasi("su@r.el", "benar", "token", buat_galat=True)
    assert str(e.value) == "Terjadi kesalahan saat memproses permintaan Anda."


def test_autentikasi_berhasil(autentikasi):
    autentikasi.lokasi = ""
    autentikasi._autentikasi("pos@el.saya", "sandi", "token")
    assert (
        autentikasi.sesi.cookies.get(".AspNet.ApplicationCookie")
        == "mockcookie"
    )
