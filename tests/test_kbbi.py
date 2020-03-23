import pytest

from kbbi import KBBI


def test_objek_auth_kelas_lain():
    with pytest.raises(ValueError) as e:
        KBBI("halo", True)
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
