def test_bin(bin):
    result = (
        "bin\n"
        "1. (n) (Ar)  kata untuk menyatakan anak laki-laki dari seseorang "
        "(biasa dipakai untuk keterangan antara nama seseorang dan nama ayah); "
        "anak laki-laki dari: Amat -- Soleh Amat anak dari Soleh\n"
        "2. (p) (cak) (Ar)  kata untuk menguatkan atau mengungkapkan dengan perkataan lain: "
        "aneh -- ajaib\n"
        "\n"
        "BIN\n"
        "(n) (sing)  Badan Intelijen Negara "
        "(lembaga pemerintah nonkementerian Indonesia yang bertugas di bidang intelijen)"
    )
    assert str(bin) == result


def test_quo_vadis(quo_vadis):
    result = (
        "quo vadis?\n"
        "(ukp) (Lt)  hendak pergi ke mana? "
        "(dipakai untuk mengingatkan seseorang agar memperbaiki dirinya)"
    )
    assert str(quo_vadis) == result


def test_civitas_academica(civitas_academica):
    result = (
        "civitas academica\n"
        "(ukp) (Lt)  kelompok (warga) masyarakat akademik yang terdiri atas dosen dan mahasiswa "
        "dengan perwakilannya yang terbentuk melalui senat masing-masing"
    )
    assert str(civitas_academica) == result


def test_khayal(khayal):
    result = (
        "kha.yal\n"
        "Bentuk tidak baku: kayal\n"
        "1. (n)  lukisan (gambar) dalam angan-angan; fantasi: apa yang diceritakan itu -- belaka\n"
        "2. (n)  yang diangan-angankan seperti benar-benar ada: cerita --"
    )
    assert str(khayal) == result


def test_semakin(semakin):
    result = "makin » se.ma.kin\n" "\n" "\n" "se.ma.kin  /sêmakin/\n" "→ makin"
    assert str(semakin) == result


def test_makin(makin):
    result = (
        "ma.kin\n"
        "Bentuk tidak baku: mangkin, semakin\n"
        "1. (adv)  kian bertambah: tangisnya -- menjadi-jadi; pesawat itu terbang -- tinggi\n"
        "2. (p) (kl)  lebih-lebih; apalagi: segala gembala gajah semuanya kasih akan Laksamana "
        "Khoja Hassan, -- kepada gembala Kepenjang itu jangan dikata lagi"
    )
    assert str(makin) == result


def test_keratabasa(keratabasa):
    result = (
        "ke.ra.ta.ba.sa  /kératabasa/\n"
        "(n)  perihal menerangkan arti kata dengan memperlakukannya sebagai singkatan, "
        "biasanya untuk lelucon (misalnya kata benci ditafsirkan sebagai ‘benar-benar cinta’); "
        "etimologi rakyat"
    )
    assert str(keratabasa) == result


def test_tampak(tampak):
    result = (
        "tam.pak [1]\n"
        "Bentuk tidak baku: nampak\n"
        "1. (v)  dapat dilihat; kelihatan: pulau itu sudah -- dari sini\n"
        "2. (v)  memperlihatkan diri; muncul: sudah lama dia tidak --\n"
        "\n"
        "tam.pak [2]\n"
        "→ campak [2]"
    )
    assert str(tampak) == result


def test_menjadikan(menjadikan):
    result = (
        "jadi [1] » men.ja.di.kan\n"
        "1. (v)  membuat sebagai; merupakan: ia ~ sakit adiknya sebagai alasan "
        "untuk tidak pergi kuliah\n"
        "2. (v)  menyebabkan: hal itu akan ~ orang lain marah-marah\n"
        "3. (v)  mengangkat (memilih) sebagai: rakyat telah ~ dia kepala desa\n"
        "4. (v)  melaksanakan (rencana, janji, dan sebagainya): ia ~ penawarannya "
        "untuk membeli rumah itu\n"
        "5. (v)  menciptakan; mengadakan: Tuhan yang ~ langit dan bumi beserta isinya"
    )
    assert str(menjadikan) == result


def test_lampir(lampir):
    result = (
        "lam.pir\n"
        "(prakategorial)  cari: lampiran, melampiri, melampirkan, terlampir"
    )
    assert str(lampir) == result


def test_kan(kan):
    result = (
        "kan [1]\n"
        "(n) (ark)  langkan (pada perahu)\n"
        "\n"
        "kan [2]\n"
        "(adv) (kp)  bukan\n"
        "\n"
        "kan [3]\n"
        "(adv) (kp)  akan\n"
        "\n"
        "kan [4]\n"
        "(n)  tempat memasak air teh; morong; teko\n"
        "\n"
        "-kan [5]\n"
        "1. (sufiks pembentuk verba)  menjadikan: jalankan; datangkan; hitamkan\n"
        "2. (sufiks pembentuk verba)  sungguh-sungguh: dengarkan; camkan\n"
        "3. (sufiks pembentuk verba)  untuk; kepada orang lain: sewakan; bacakan"
    )
    assert str(kan) == result


def test_me_(me_):
    result = (
        "me-  /mê-/\n"
        "→ meng-\n"
        "\n"
        "meng-  /mêng-/\n"
        "Varian: me-, mem-, men-, menge-, meny-\n"
        "1. (prefiks pembentuk verba)  menjadi: mencair; menguning; mengkristal\n"
        "2. (prefiks pembentuk verba)  berfungsi sebagai atau menyerupai: menyupir; menggunung\n"
        "3. (prefiks pembentuk verba)  makan atau minum: menyatai; mengopi; mengeteh\n"
        "4. (prefiks pembentuk verba)  menuju: mengutara; melaut; menepi\n"
        "5. (prefiks pembentuk verba)  mencari atau mengumpulkan: mendamar; merumput\n"
        "6. (prefiks pembentuk verba)  mengeluarkan bunyi: mengeong; mengaum; mencicit\n"
        "7. (prefiks pembentuk verba)  menimbulkan kesan seperti seseorang atau sesuatu yang: membisu; membatu; merendah hati\n"
        "8. (prefiks pembentuk verba)  dasar verba: membaca; menulis; membajak\n"
        "9. (prefiks pembentuk verba)  membuat; menghasilkan: menyambal; menggulai; membatik\n"
        "10. (prefiks pembentuk verba)  menyatakan: mengaku"
    )
    assert str(me_) == result


def test__kan(_kan):
    result = (
        "-kan [5]\n"
        "1. (sufiks pembentuk verba)  menjadikan: jalankan; datangkan; hitamkan\n"
        "2. (sufiks pembentuk verba)  sungguh-sungguh: dengarkan; camkan\n"
        "3. (sufiks pembentuk verba)  untuk; kepada orang lain: sewakan; bacakan"
    )
    assert str(_kan) == result


def test__lah(_lah):
    result = (
        "-lah [1]\n"
        "(bentuk terikat)  yang digunakan untuk menekankan makna kata yang di depannya"
    )
    assert str(_lah) == result
