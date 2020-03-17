def str(entri):
    return entri.__str__(contoh=False)


def test_bin(bin):
    result = (
        "bin\n"
        "1. (n) (Ar)  kata untuk menyatakan anak laki-laki dari seseorang "
        "(biasa dipakai untuk keterangan antara nama seseorang dan nama ayah); "
        "anak laki-laki dari\n"
        "2. (p) (cak) (Ar)  kata untuk menguatkan atau mengungkapkan dengan perkataan lain\n"
        "\n"
        "BIN\n"
        "(n) (sing)  Badan Intelijen Negara "
        "(lembaga pemerintah nonkementerian Indonesia yang bertugas di bidang intelijen)"
    )
    assert str(bin) == result


def test_khayal(khayal):
    result = (
        "kha.yal\n"
        "Bentuk tidak baku: kayal\n"
        "1. (n)  lukisan (gambar) dalam angan-angan; fantasi\n"
        "2. (n)  yang diangan-angankan seperti benar-benar ada"
    )
    assert str(khayal) == result


def test_makin(makin):
    result = (
        "ma.kin\n"
        "Bentuk tidak baku: mangkin, semakin\n"
        "1. (adv)  kian bertambah\n"
        "2. (p) (kl)  lebih-lebih; apalagi"
    )
    assert str(makin) == result


def test_tampak(tampak):
    result = (
        "tam.pak (1)\n"
        "Bentuk tidak baku: nampak\n"
        "1. (v)  dapat dilihat; kelihatan\n"
        "2. (v)  memperlihatkan diri; muncul\n"
        "\n"
        "tam.pak (2)\n"
        "→ campak (2)"
    )
    assert str(tampak) == result


def test_menjadikan(menjadikan):
    result = (
        "jadi (1) » men.ja.di.kan\n"
        "1. (v)  membuat sebagai; merupakan\n"
        "2. (v)  menyebabkan\n"
        "3. (v)  mengangkat (memilih) sebagai\n"
        "4. (v)  melaksanakan (rencana, janji, dan sebagainya)\n"
        "5. (v)  menciptakan; mengadakan"
    )
    assert str(menjadikan) == result


def test_prakategorial_lampir(lampir):
    result = (
        "lam.pir\n"
        "(prakategorial)  cari: lampiran, melampiri, melampirkan, terlampir"
    )
    assert str(lampir) == result


def test_kan(kan):
    result = (
        "kan (1)\n"
        "(n) (ark)  langkan (pada perahu)\n"
        "\n"
        "kan (2)\n"
        "(adv) (kp)  bukan\n"
        "\n"
        "kan (3)\n"
        "(adv) (kp)  akan\n"
        "\n"
        "kan (4)\n"
        "(n)  tempat memasak air teh; morong; teko\n"
        "\n"
        "-kan (5)\n"
        "1. (sufiks pembentuk verba)  menjadikan\n"
        "2. (sufiks pembentuk verba)  sungguh-sungguh\n"
        "3. (sufiks pembentuk verba)  untuk; kepada orang lain"
    )
    assert str(kan) == result


def test_awalan_me(awalan_me):
    result = (
        "me-  /mê-/\n"
        "→ meng-\n"
        "\n"
        "meng-  /mêng-/\n"
        "Varian: me-, mem-, men-, menge-, meny-\n"
        "1. (prefiks pembentuk verba)  menjadi\n"
        "2. (prefiks pembentuk verba)  berfungsi sebagai atau menyerupai\n"
        "3. (prefiks pembentuk verba)  makan atau minum\n"
        "4. (prefiks pembentuk verba)  menuju\n"
        "5. (prefiks pembentuk verba)  mencari atau mengumpulkan\n"
        "6. (prefiks pembentuk verba)  mengeluarkan bunyi\n"
        "7. (prefiks pembentuk verba)  menimbulkan kesan seperti seseorang atau sesuatu yang\n"
        "8. (prefiks pembentuk verba)  dasar verba\n"
        "9. (prefiks pembentuk verba)  membuat; menghasilkan\n"
        "10. (prefiks pembentuk verba)  menyatakan"
    )
    assert str(awalan_me) == result


def test_akhiran_kan(akhiran_kan):
    result = (
        "-kan (5)\n"
        "1. (sufiks pembentuk verba)  menjadikan\n"
        "2. (sufiks pembentuk verba)  sungguh-sungguh\n"
        "3. (sufiks pembentuk verba)  untuk; kepada orang lain"
    )
    assert str(akhiran_kan) == result
