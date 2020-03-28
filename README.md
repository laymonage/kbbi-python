# kbbi-python

[![pypi][pypi-badge]][pypi-package]
[![license][license-badge]][LICENSE]
[![Test][test-badge]][github-actions]
[![coverage][coverage-badge]][coveralls]
[![black][black-badge]][black]


Modul Python untuk mengambil sebuah laman untuk kata/frasa dalam
[KBBI Daring][kbbi].

## Instalasi

### Melalui pip

```bash
pip install kbbi
```

### Manual

1. Lakukan instalasi untuk paket-paket prasyarat ([`requests`][requests]
   dan [`BeautifulSoup4`][beautifulsoup4]).
2. Klonakan repositori ini atau unduh [`kbbi.py`][kbbi-py].
3. Letakkan `kbbi.py` dalam direktori yang Anda inginkan.

## Penggunaan

### Melalui kode Python

Buat objek `KBBI` baru (contoh: `kata = KBBI('kata kunci')`), lalu manfaatkan
representasi `str`-nya dengan memanggil `str(kata)` atau ambil `dict` hasil
serialisasinya dengan memanggil `kata.serialisasi()`. Apabila ingin memanfaatkan
representasi `str`-nya tanpa contoh (jika ada), gunakan `__str__(contoh=False)`.

Untuk lebih jelasnya, lihat contoh berikut.

```python
>>> from kbbi import KBBI
>>> cinta = KBBI('cinta')
>>> print(cinta)
cin.ta
1. (a)  suka sekali; sayang benar: orang tuaku -- kepada kami semua; -- kepada sesama makhluk
2. (a)  kasih sekali; terpikat (antara laki-laki dan perempuan): sebenarnya dia tidak -- kepada lelaki itu, tetapi hanya menginginkan hartanya
3. (a)  ingin sekali; berharap sekali; rindu: makin ditindas makin terasa betapa --nya akan kemerdekaan
4. (a) (kl)  susah hati (khawatir); risau: tiada terperikan lagi --nya ditinggalkan ayahnya itu
>>> print(cinta.__str__(contoh=False))
cin.ta
1. (a)  suka sekali; sayang benar
2. (a)  kasih sekali; terpikat (antara laki-laki dan perempuan)
3. (a)  ingin sekali; berharap sekali; rindu
4. (a) (kl)  susah hati (khawatir); risau
```

```python
>>> kata = KBBI('taksir')
>>> print(kata)
tak.sir (1)
(n)  kira-kira; hitungan (kasar)

tak.sir (2)
1. (a) (Ar)  tidak mengindahkan; lalai; alpa
2. (n) (Ar)  kelalaian; kealpaan
>>> import json
>>> print(json.dumps(kata.serialisasi(), indent=2))
{
  "pranala": "https://kbbi.kemdikbud.go.id/entri/taksir",
  "entri": [
    {
      "nama": "tak.sir",
      "nomor": "1",
      "kata_dasar": [],
      "pelafalan": "",
      "bentuk_tidak_baku": [],
      "varian": [],
      "makna": [
        {
          "kelas": [
            {
              "kode": "n",
              "nama": "Nomina",
              "deskripsi": "kata benda"
            }
          ],
          "submakna": [
            "kira-kira",
            "hitungan (kasar)"
          ],
          "info": "",
          "contoh": []
        }
      ]
    },
    {
      "nama": "tak.sir",
      "nomor": "2",
      "kata_dasar": [],
      "pelafalan": "",
      "bentuk_tidak_baku": [],
      "varian": [],
      "makna": [
        {
          "kelas": [
            {
              "kode": "a",
              "nama": "Adjektiva",
              "deskripsi": "kata yang menjelaskan nomina atau pronomina"
            },
            {
              "kode": "Ar",
              "nama": "Arab",
              "deskripsi": "-"
            }
          ],
          "submakna": [
            "tidak mengindahkan",
            "lalai",
            "alpa"
          ],
          "info": "",
          "contoh": []
        },
        {
          "kelas": [
            {
              "kode": "n",
              "nama": "Nomina",
              "deskripsi": "kata benda"
            },
            {
              "kode": "Ar",
              "nama": "Arab",
              "deskripsi": "-"
            }
          ],
          "submakna": [
            "kelalaian",
            "kealpaan"
          ],
          "info": "",
          "contoh": []
        }
      ]
    }
  ]
}
```

Untuk memanfaatkan fitur khusus pengguna, buat objek `AutentikasiKBBI` terlebih
dahulu, lalu gunakan objek tersebut dalam pembuatan objek `KBBI`.

```python
>>> auth = AutentikasiKBBI("posel@saya.tld", "password_saya")
>>> roh = KBBI("roh", auth)
>>> print(roh)
roh
bentuk tidak baku: ruh
Etimologi: [Arab] (n) (sg) (f/m)  رُوْحٌ rūh: tiupan; sesuatu yang membuat manusia dapat hidup
1. (n)  sesuatu (unsur) yang ada dalam jasad yang diciptakan Tuhan sebagai penyebab adanya hidup (kehidupan); nyawa: jika -- sudah berpisah dari badan, berakhirlah kehidupan seseorang
2. (n)  makhluk hidup yang tidak berjasad, tetapi berpikiran dan berperasaan (malaikat, jin, setan, dan sebagainya)
3. (n) (ki)  semangat; spirit: kedamaian bagi seluruh warga sesuai dengan -- Islam
Gabungan Kata
roh Kudus; roh suci
```

Fitur khusus pengguna yang didukung saat ini adalah etimologi, entri terkait
(kata turunan, gabungan kata, peribahasa, dan kiasan), dan batas pencarian yang
lebih besar.

Untuk mendapatkan representasi `str`-nya tanpa fitur entri terkait, gunakan
`__str__(terkait=False)`.

```python
>>> print(roh.__str__(contoh=False, terkait=False))
roh
bentuk tidak baku: ruh
Etimologi: [Arab] (n) (sg) (f/m)  رُوْحٌ rūh: tiupan; sesuatu yang membuat manusia dapat hidup
1. (n)  sesuatu (unsur) yang ada dalam jasad yang diciptakan Tuhan sebagai penyebab adanya hidup (kehidupan); nyawa
2. (n)  makhluk hidup yang tidak berjasad, tetapi berpikiran dan berperasaan (malaikat, jin, setan, dan sebagainya)
3. (n) (ki)  semangat; spirit
```

Untuk menonaktifkan fitur khusus pengguna (selain batas pencarian yang lebih
besar), tambahkan argumen `fitur_pengguna=False` pada pemanggilan `__str__`
atau `serialisasi`.

Apabila ingin menyimpan kuki autentikasi, panggil *method* `simpan_kuki()` pada
objek `AutentikasiKBBI`.

```python
>>> auth.simpan_kuki()
```

Berikutnya, objek `AutentikasiKBBI` dapat dibuat tanpa menggunakan alamat posel
dan sandi. Autentikasi dilakukan dengan memanfaatkan kuki yang telah disimpan.

```python
>>> auth_baru = AutentikasiKBBI()
```

Lokasi penyimpanan/pembacaan kuki bisa diatur dengan parameter `lokasi_kuki`
ketika membuat objek `AutentikasiKBBI`.

```python
>>> auth = AutentikasiKBBI("posel@saya.tld", "sandi_saya", lokasi_kuki="~/kuki_kbbi.json")
>>> auth_baru = AutentikasiKBBI(lokasi_kuki="~/kuki_kbbi.json")
```

Secara *default*, lokasi tersebut adalah:

- Unix: `~/.config/kbbi/kuki.json`
- Windows: `%localappdata%\laymonage\kbbi\kuki.json`
- Mac: `~/Library/Application Support/kbbi/kuki.json`

### Melalui CLI

```
$ kbbi cinta
```

Pencarian dengan kata/frasa yang dipisahkan oleh spasi harus diapit oleh
tanda petik.

```
$ kbbi "tanggung jawab"
```

Apabila tidak ingin menampilkan contoh, gunakan `--tanpa-contoh` atau `-c`.

```
$ kbbi "tanggung jawab" --tanpa-contoh
```

Untuk mendapatkan hasil dalam bentuk serialisasi JSON, gunakan `--json`
atau `-j`.

```
$ kbbi "tanggung jawab" --json
```

Untuk mengatur indentasi pada serialisasi JSON, gunakan `--indentasi N`
atau `-i N`.

```
$ kbbi "tanggung jawab" --json --indentasi 2
```

Untuk memanfaatkan fitur khusus pengguna, lakukan autentikasi terlebih dahulu
dengan bantuan `kbbi-autentikasi`.

```
$ kbbi-autentikasi $KBBI_POSEL $KBBI_SANDI
```

Penggunaan `kbbi` berikutnya akan otomatis menggunakan kuki hasil autentikasi.

Untuk menonaktifkan fitur entri terkait, gunakan `--tanpa-terkait` atau `-t`.

```
$ kbbi alam --tanpa-terkait
```

Untuk menonaktifkan semua fitur khusus pengguna (selain batas pencarian yang
lebih besar dan tanpa menghapus kuki), gunakan `--nonpengguna` atau `-n`.

```
$ kbbi alam --nonpengguna
```

Untuk menghapus kuki, gunakan opsi `--bersihkan` atau `-c`.

```
$ kbbi-autentikasi --bersihkan
```

Gunakan opsi `--lokasi-kuki` atau `-l` untuk menentukan lokasi kuki yang akan
disimpan/dimuat.

```
$ kbbi-autentikasi $KBBI_POSEL $KBBI_SANDI --lokasi-kuki kukiku.json
$ kbbi alam --lokasi-kuki kukiku.json
```

> **Catatan:**\
> **`kbbi`** juga bisa dipanggil dengan **`python kbbi.py`**.\
> **`kbbi-autentikasi`** juga bisa dipanggil dengan **`python -c "import kbbi; kbbi.autentikasi()"`**

## Berkontribusi

Silakan lihat [CONTRIBUTING.md][CONTRIBUTING.md].

## Lisensi

Proyek ini didistribusikan dengan lisensi [MIT][license].

## Penafian

Proyek ini merupakan proyek pribadi yang didasari oleh rasa cinta kepada
bahasa Indonesia dan bahasa pemrograman Python. Proyek ini bertujuan untuk
memudahkan akses ke KBBI daring tanpa menggunakan peramban web. Proyek ini
tidak dimaksudkan untuk menyalahi [hak cipta KBBI daring][hukum]. Proyek ini
dan pengembangnya tidak berafiliasi dengan
[Badan Bahasa Kemdikbud][badan-bahasa] maupun
[Python Software Foundation][psf]. Pengembang tidak bertanggung jawab atas
penyalahgunaan yang mungkin muncul dari proyek ini.

[pypi-badge]: https://img.shields.io/pypi/v/kbbi
[pypi-package]: https://pypi.org/project/kbbi
[license-badge]: https://img.shields.io/pypi/l/kbbi
[test-badge]: https://github.com/laymonage/kbbi-python/workflows/Test/badge.svg
[github-actions]: http://github.com/laymonage/kbbi-python/actions
[coverage-badge]: https://coveralls.io/repos/github/laymonage/kbbi-python/badge.svg
[coveralls]: https://coveralls.io/r/laymonage/kbbi-python
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black]: https://github.com/psf/black
[kbbi]: https://kbbi.kemdikbud.go.id
[requests]: https://pypi.org/project/requests
[beautifulsoup4]: https://pypi.org/project/beautifulsoup4
[kbbi-py]: kbbi/kbbi.py
[CONTRIBUTING.md]: CONTRIBUTING.md
[license]: LICENSE
[hukum]: https://kbbi.kemdikbud.go.id/Beranda/Hukum
[badan-bahasa]: http://badanbahasa.kemdikbud.go.id
[psf]: https://www.python.org/psf
