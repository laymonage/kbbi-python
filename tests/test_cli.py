import sys as _sys

import pytest

import kbbi


def test_bersihkan_kuki_tidak_ada(mock_lokasi_kuki, tanpa_kuki, capsys):
    hasil = kbbi.autentikasi(["--bersihkan"])
    tangkap = capsys.readouterr()
    assert tangkap.out == "Kuki tidak ditemukan pada kukifix.json!\n"
    assert hasil == 1


def test_bersihkan_kuki_ada(kuki, capsys):
    hasil = kbbi.autentikasi(["--bersihkan"])
    tangkap = capsys.readouterr()
    assert tangkap.out == "Kuki kukifix.json berhasil dihapus.\n"
    assert hasil == 0


def test_autentikasi_tanpa_argumen_sama_dengan_bantuan(monkeypatch, capsys):
    monkeypatch.setattr(_sys, "exit", lambda x: None)
    monkeypatch.setattr(_sys, "argv", ["kbbi-autentikasi"])
    kbbi.autentikasi(["--bantuan"])
    tangkap = capsys.readouterr()
    bantuan = tangkap.out
    hasil = kbbi.autentikasi()
    tangkap = capsys.readouterr()
    assert tangkap.out == bantuan
    assert hasil == 0


def test_autentikasi_gagal(autentikasi_gagal, capsys):
    hasil = kbbi.autentikasi(["posel@saya.tld", "sandi_saya"])
    tangkap = capsys.readouterr()
    assert tangkap.out == (
        "Gagal melakukan autentikasi dengan alamat posel dan sandi "
        "yang diberikan.\n"
    )
    assert hasil == 1


def test_autentikasi_sukses(autentikasi_sukses, mock_lokasi_kuki, capsys):
    hasil = kbbi.autentikasi(["posel@saya.tld", "p4sti_sukses"])
    tangkap = capsys.readouterr()
    assert tangkap.out == (
        "Autentikasi berhasil dan kuki telah disimpan di kukifix.json.\n"
        "Kuki akan otomatis digunakan pada penggunaan KBBI berikutnya.\n"
    )
    assert hasil == 0
    assert (
        mock_lokasi_kuki.read_text()
        == '{".AspNet.ApplicationCookie": "mockcookie"}'
    )
    mock_lokasi_kuki.unlink()


def test_autentikasi_sukses_dengan_lokasi_kuki(
    autentikasi_sukses, lokasi_kuki, capsys
):
    hasil = kbbi.autentikasi(
        ["posel@saya.tld", "p4sti_sukses", "--lokasi-kuki", "kukifix.json"]
    )
    tangkap = capsys.readouterr()
    assert tangkap.out == (
        "Autentikasi berhasil dan kuki telah disimpan di kukifix.json.\n"
        "Kuki akan otomatis digunakan pada penggunaan KBBI berikutnya.\n"
        "Gunakan opsi --lokasi-kuki yang sama ketika menggunakan KBBI.\n"
    )
    assert hasil == 0
    assert (
        lokasi_kuki.read_text()
        == '{".AspNet.ApplicationCookie": "mockcookie"}'
    )
    lokasi_kuki.unlink()


@pytest.mark.parametrize(
    "kbbi_mock,lokasi", [(None, "kasus/nonauth/str/alam.txt")], indirect=True
)
def test_program_utama_tanpa_kuki_str_sukses(
    capsys, kbbi_mock, lokasi, tanpa_kuki
):
    hasil = kbbi.main(["alam"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi", [(None, "kasus/nonauth/str/alam.txt")], indirect=True
)
def test_program_utama_dengan_kuki_nonpengguna_str_sukses(
    capsys, kbbi_mock, lokasi, kuki
):
    hasil = kbbi.main(["alam", "--nonpengguna"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi",
    [(None, "kasus/nonauth/str_tanpa_contoh/alam.txt")],
    indirect=True,
)
def test_program_utama_tanpa_kuki_str_tanpa_contoh_sukses(
    capsys, kbbi_mock, lokasi, tanpa_kuki
):
    hasil = kbbi.main(["alam", "--tanpa-contoh"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi",
    [(None, "kasus/nonauth/serialisasi/alam.json")],
    indirect=True,
)
def test_program_utama_tanpa_kuki_json_sukses(
    capsys, kbbi_mock, lokasi, tanpa_kuki
):
    hasil = kbbi.main(["alam", "--json", "--indentasi", "2"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi", [("auth", "kasus/auth/str/alam.txt")], indirect=True
)
def test_program_utama_dengan_kuki_str_sukses(capsys, kbbi_mock, lokasi, kuki):
    hasil = kbbi.main(["alam"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi",
    [("auth", "kasus/auth/str_tanpa_contoh/alam.txt")],
    indirect=True,
)
def test_program_utama_dengan_kuki_str_tanpa_contoh_sukses(
    capsys, kbbi_mock, lokasi, kuki
):
    hasil = kbbi.main(["alam", "--tanpa-contoh"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock,lokasi",
    [("auth", "kasus/auth/serialisasi/alam.json")],
    indirect=True,
)
def test_program_utama_dengan_kuki_json_sukses(
    capsys, kbbi_mock, lokasi, kuki
):
    hasil = kbbi.main(["alam", "--json", "--indentasi", "2"])
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize(
    "kbbi_mock", [(None, "Beranda/Error.html")], indirect=True
)
def test_program_utama_gagal(capsys, kbbi_mock):
    hasil = kbbi.main(["lampir"])
    tangkap = capsys.readouterr()
    assert tangkap.out == (
        "Terjadi kesalahan saat memproses permintaan Anda.\n"
    )
    assert hasil == 1


@pytest.mark.parametrize(
    "kbbi_mock,lokasi", [(None, "kasus/nonauth/str/alam.txt")], indirect=True
)
def test_program_utama_main(
    monkeypatch, capsys, kbbi_mock, lokasi, tanpa_kuki
):
    monkeypatch.setattr(_sys, "exit", lambda x: x)
    monkeypatch.setattr(_sys, "argv", ["kbbi", "alam"])
    monkeypatch.setattr(kbbi.kbbi, "__name__", "__main__")
    hasil = kbbi.init()
    tangkap = capsys.readouterr()
    assert tangkap.out == lokasi.read_text()
    assert hasil == 0


@pytest.mark.parametrize("kbbi_mock", [None], indirect=True)
def test_program_utama_lokasi_kuki_tidak_ada(capsys, kbbi_mock, tanpa_kuki):
    hasil = kbbi.main(["alam", "--lokasi-kuki", "kukiku.json"])
    tangkap = capsys.readouterr()
    assert tangkap.out == "Kuki tidak ditemukan pada kukiku.json!\n"
    assert hasil == 1
