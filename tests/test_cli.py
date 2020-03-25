import pathlib

import kbbi


def test_bersihkan_kuki_tidak_ada(monkeypatch, capsys):
    lokasi_kuki = pathlib.Path("kuki.json")
    assert not lokasi_kuki.exists()
    monkeypatch.setattr(kbbi.AutentikasiKBBI, "lokasi_kuki", lokasi_kuki)
    hasil = kbbi.autentikasi(["--bersihkan"])
    tangkap = capsys.readouterr()
    assert tangkap.out == "Kuki tidak ditemukan pada kuki.json!\n"
    assert hasil == 1


def test_bersihkan_kuki_ada(monkeypatch, capsys):
    lokasi_kuki = pathlib.Path("kukiku.json")
    lokasi_kuki.write_text("kukiku enak\n")
    monkeypatch.setattr(kbbi.AutentikasiKBBI, "lokasi_kuki", lokasi_kuki)
    hasil = kbbi.autentikasi(["--bersihkan"])
    tangkap = capsys.readouterr()
    assert tangkap.out == "Kuki kukiku.json berhasil dihapus.\n"
    assert hasil == 0
