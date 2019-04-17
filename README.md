# kbbi-python

Modul Python untuk mengambil sebuah laman untuk kata/frasa dalam [KBBI Daring][kbbi].

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
```

```python
>>> kata = KBBI('taksir')
>>> print(kata)
tak.sir [1]
(n)  kira-kira; hitungan (kasar)

tak.sir [2]
1. (a) (Ar)  tidak mengindahkan; lalai; alpa
2. (n) (Ar)  kelalaian; kealpaan
>>> import json
>>> print(json.dumps(kata.serialisasi(), indent=2))
{
  "taksir": [
    {
      "nama": "tak.sir",
      "nomor": "1",
      "kata_dasar": [],
      "pelafalan": "",
      "bentuk_tidak_baku": [],
      "varian": [],
      "makna": [
        {
          "kelas": {
            "n": "Nomina: kata benda"
          },
          "submakna": [
            "kira-kira",
            "hitungan (kasar)"
          ],
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
          "kelas": {
            "a": "Adjektiva: kata yang menjelaskan nomina atau pronomina",
            "Ar": "Arab: -"
          },
          "submakna": [
            "tidak mengindahkan",
            "lalai",
            "alpa"
          ],
          "contoh": []
        },
        {
          "kelas": {
            "n": "Nomina: kata benda",
            "Ar": "Arab: -"
          },
          "submakna": [
            "kelalaian",
            "kealpaan"
          ],
          "contoh": []
        }
      ]
    }
  ]
}
```

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

[kbbi]: https://kbbi.kemdikbud.go.id
[requests]: https://pypi.org/project/requests
[beautifulsoup4]: https://pypi.org/project/requests/beautifulsoup4
[kbbi-py]: kbbi/kbbi.py
[license]: LICENSE
[hukum]: https://kbbi.kemdikbud.go.id/Beranda/Hukum
[badan-bahasa]: http://badanbahasa.kemdikbud.go.id
[psf]: https://www.python.org/psf
