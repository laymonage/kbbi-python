"""
:mod:`kbbi` -- Modul KBBI Python
================================

.. module:: kbbi
   :platform: Unix, Windows, Mac
   :synopsis: Modul ini mengandung implementasi dari modul kbbi.
.. moduleauthor:: sage <laymonage@gmail.com>
"""

import argparse
import json
import sys
import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

__CHROME_UA__ = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'


class KBBI:
    """Sebuah laman dalam KBBI daring."""

    host = "https://kbbi.kemdikbud.go.id"

    def __init__(self, kueri, email, password):
        """Membuat objek KBBI baru berdasarkan kueri yang diberikan.

        :param kueri: Kata kunci pencarian
        :type kueri: str
        :param email: Alamat surel yang terdaftar di KBBI
        :type email: str
        :param password: Kata sandi dari alamat surel yang terdaftar
        :type password: str
        """
        self.nama = kueri
        self.terautentikasi = False
        self._init_pranala()
        self.sesi = requests.Session()
        self.sesi.headers.update(
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
            }
        )
        if email and password:
            self._autentikasi(email, password)
        laman = self.sesi.get(self.pranala)
        self._cek_galat(laman)
        self._init_entri(laman)

    def _init_pranala(self):
        kasus_khusus = [
            "." in self.nama,
            "?" in self.nama,
            self.nama.lower() == "nul",
            self.nama.lower() == "bin",
        ]
        if any(kasus_khusus):
            self.pranala = f"{self.host}/Cari/Hasil?frasa={quote(self.nama)}"
        else:
            self.pranala = f"{self.host}/entri/{quote(self.nama)}"

    def _cek_galat(self, laman):
        if "Beranda/Error" in laman.url:
            raise TerjadiKesalahan()
        if "Beranda/BatasSehari" in laman.url:
            raise BatasSehari()
        if "Entri tidak ditemukan." in laman.text:
            raise TidakDitemukan(self.nama)

    def _autentikasi(self, email, password):
        """
        Melakukan autentikasi dengan surel dan sandi yang diberikan.
        Berguna untuk mendapatkan segala fitur pengguna terdaftar

        :param email: Alamat surel yang terdaftar di KBBI
        :type email: str
        :param password: Kata sandi dari alamat surel yang terdaftar
        :type password: str
        """
        laman = self.sesi.get(f"{self.host}/Account/Login") # Dapatkan __RequestVerificationToken.
        token = re.findall(r"<input name=\"__RequestVerificationToken\".*value=\"(.*)\" />", laman.text)
        if not token:
            raise TerjadiKesalahan()
        payload = {
            "__RequestVerificationToken": token[0],
            "Posel": email,
            "KataSandi": password,
            "IngatSaya": True,
            "IngatSaya": False
        }
        laman = self.sesi.post(
            f"{self.host}/Account/Login",
            data=payload
        )
        if 'Beranda/Error' in laman.url:
            raise GagalAutentikasi()
        self.terautentikasi = True

    def _init_entri(self, laman):
        sup = BeautifulSoup(laman.text, "html.parser")
        estr = ""
        self.entri = []
        for label in sup.find("hr").next_siblings:
            if label.name == "hr":
                if label.get("style") is None:
                    self.entri.append(Entri(estr))
                    break
                else:
                    continue
            if label.name == "h2":
                if label.get("style") == "color:gray":
                    continue
                if estr:
                    self.entri.append(Entri(estr))
                estr = ""
            estr += str(label).strip()

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek KBBI ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """
        return {
            "pranala": self.pranala,
            "entri": [entri.serialisasi() for entri in self.entri],
        }

    def __str__(self, contoh=True):
        return "\n\n".join(
            entri.__str__(contoh=contoh) for entri in self.entri
        )

    def __repr__(self):
        return f"<KBBI: {self.nama}>"


class Entri:
    """Sebuah entri dalam sebuah laman KBBI daring."""

    def __init__(self, entri_html):
        entri = BeautifulSoup(entri_html, "html.parser")
        judul = entri.find("h2")
        self.terautentikasi = False
        self._cek_autentikasi(entri)
        self._init_nama(judul)
        self._init_nomor(judul)
        self._init_kata_dasar(judul)
        self._init_pelafalan(judul)
        self._init_varian(judul)
        self._init_lain_lain(entri)
        self._init_etimologi(entri)
        self._init_makna(entri)

    def _cek_autentikasi(self, entri):
        all_href = [ehref['href'] for ehref in entri.find_all('a') if ehref.get('href', None)]
        for href in all_href:
            if "DataDasarEntri" in href:
                self.terautentikasi = True
                break

    def _init_nama(self, judul):
        self.nama = ambil_teks_dalam_label(judul, ambil_italic=True)
        if not self.nama:
            self.nama = judul.find_all(text=True)[0].strip()

    def _init_nomor(self, judul):
        nomor = judul.find("sup", recursive=False)
        self.nomor = nomor.text.strip() if nomor else ""

    def _init_kata_dasar(self, judul):
        dasar = judul.find_all(class_="rootword")
        self.kata_dasar = []
        for tiap in dasar:
            kata = tiap.find("a")
            dasar_no = kata.find("sup")
            kata = ambil_teks_dalam_label(kata)
            self.kata_dasar.append(
                f"{kata} ({dasar_no.text.strip()})" if dasar_no else kata
            )

    def _init_pelafalan(self, judul):
        lafal = judul.find(class_="syllable")
        self.pelafalan = lafal.text.strip() if lafal else ""

    def _init_varian(self, judul):
        if self.terautentikasi:
            variasi = judul.find_all('small')
            varian = None
            for v in variasi:
                spanv = v.find('span')
                if spanv:
                    if spanv.get('class'):
                        if "entrisButton" in spanv['class']:
                            continue
                varian = v
        else:
            varian = judul.find("small")
        self.bentuk_tidak_baku = []
        self.varian = []
        if varian:
            bentuk_tidak_baku = varian.find_all("b")
            if bentuk_tidak_baku:
                self.bentuk_tidak_baku = "".join(
                    e.text.strip() for e in bentuk_tidak_baku
                ).split(", ")
            else:
                self.varian = (
                    varian.text[len("varian: ") :].strip().split(", ")
                )

    def _init_etimologi(self, entri):
        self.etimologi = None
        if not self.terautentikasi:
            return
        etimologi = entri.find_all('b') # , {"style": "margin-left:19px"}
        if etimologi:
            for etimo in etimologi:
                if "Etimologi" in etimo.text:
                    etistr = ""
                    for eti in etimo.next_siblings:
                        if eti.name == "br":
                            break
                        etistr += str(eti).strip()
                    self.etimologi = Etimologi(etistr)
                    break

    def _init_lain_lain(self, entri):
        self.kata_turunan = []
        self.gabungan_kata = []
        self.peribahasa = []
        if not self.terautentikasi:
            return
        lain_lain = entri.find_all('h4')
        kata_turunan = None
        gabungan_kata = None
        peribahasa = None
        for le in lain_lain:
            if le:
                le_txt = le.text.strip()
                if "Kata Turunan" in le_txt:
                    kata_turunan = le
                if "Gabungan Kata" in le_txt:
                    gabungan_kata = le
                if "Peribahasa" in le_txt:
                    peribahasa = le
        if kata_turunan:
            kata_turunan = kata_turunan.next_sibling
            if kata_turunan:
                kata_turunan = kata_turunan.find_all('a')
                self.kata_turunan = [kt.text for kt in kata_turunan if kt]
        if gabungan_kata:
            gabungan_kata = gabungan_kata.next_sibling
            if gabungan_kata:
                gabungan_kata = gabungan_kata.find_all('a')
                self.gabungan_kata = [gk.text for gk in gabungan_kata if gk]
        if peribahasa:
            peribahasa = peribahasa.next_sibling
            if peribahasa:
                peribahasa = peribahasa.find_all('a')
                self.peribahasa = [p.text for p in peribahasa if p]

    def _init_makna(self, entri):
        if entri.find(color="darkgreen"):
            makna = [entri]
        else:
            makna = entri.find_all("li")
        if self.terautentikasi:
            old_makna = makna
            makna = []
            for om in old_makna:
                if om:
                    if "Usulkan makna baru" in om.text:
                        continue
                    makna.append(om)
            del old_makna
        if self.peribahasa:
            makna = makna[:-1]
        if self.gabungan_kata:
            makna = makna[:-1]
        if self.kata_turunan:
            makna = makna[:-1]
        self.makna = [Makna(m) for m in makna]

    def serialisasi(self):
        return {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "etimologi": self.etimologi.serialisasi() if self.etimologi else None,
            "makna": [makna.serialisasi() for makna in self.makna],
            "kata_turunan": self.kata_turunan,
            "gabungan_kata": self.gabungan_kata,
            "peribahasa": self.peribahasa
        }

    def _makna(self, contoh=True):
        if len(self.makna) > 1:
            return "\n".join(
                f"{i}. {makna.__str__(contoh=contoh)}"
                for i, makna in enumerate(self.makna, 1)
            )
        if len(self.makna) == 1:
            return self.makna[0].__str__(contoh=contoh)
        return ""

    def _nama(self):
        hasil = self.nama
        if self.nomor:
            hasil += f" ({self.nomor})"
        if self.kata_dasar:
            hasil = f"{' » '.join(self.kata_dasar)} » {hasil}"
        return hasil

    def _varian(self, varian):
        if varian == self.bentuk_tidak_baku:
            nama = "bentuk tidak baku"
        elif varian == self.varian:
            nama = "varian"
        else:
            return ""
        return f"{nama}: {', '.join(varian)}"

    def __str__(self, contoh=True):
        hasil = self._nama()
        if self.pelafalan:
            hasil += f"  {self.pelafalan}"
        for var in (self.bentuk_tidak_baku, self.varian):
            if var:
                hasil += f"\n{self._varian(var)}"
        if self.etimologi:
            hasil += f"\nEtimologi: {self.etimologi.__str__()}"
        hasil += f"\n{self._makna(contoh)}"
        if self.kata_turunan:
            hasil += f"\nKata Turunan: {'; '.join(self.kata_turunan)}"
        if self.gabungan_kata:
            hasil += f"\nGabungan Kata: {'; '.join(self.gabungan_kata)}"
        if self.peribahasa:
            hasil += f"\nPeribahasa (mengandung [{self.nama}]): {', '.join(self.peribahasa)}"
        return hasil

    def __repr__(self):
        return f"<Entri: {self._nama()}>"


class Makna:
    """Sebuah makna dalam sebuah entri KBBI daring."""

    def __init__(self, makna_label):
        self._init_submakna(makna_label)
        self._init_kelas(makna_label)
        self._init_contoh(makna_label)
        self.submakna = self.submakna.split("; ")

    def _init_submakna(self, makna_label):
        baku = makna_label.find("a")
        if baku:
            self.submakna = f"→ {ambil_teks_dalam_label(baku)}"
            nomor = baku.find("sup")
            if nomor:
                self.submakna += f" ({nomor.text.strip()})"
        else:
            self.submakna = (
                "".join(
                    i.string for i in makna_label.contents if i.name != "font"
                )
                .strip()
                .rstrip(":")
            )

    def _init_kelas(self, makna_label):
        kelas = makna_label.find(color="red")
        lain = makna_label.find(color="darkgreen")
        info = makna_label.find(color="green")

        if kelas:
            kelas = kelas.find_all("span")
        if lain:
            kelas = [lain]
            self.submakna = lain.next_sibling.strip()
            self.submakna += (
                f" {makna_label.find(color='grey').get_text().strip()}"
            )

        self.kelas = []
        for k in kelas:
            kode = k.text.strip()
            pisah = k["title"].strip().split(": ")
            nama = pisah[0].strip()
            deskripsi = pisah[1].strip() if len(pisah) > 1 else ""
            self.kelas.append(
                {"kode": kode, "nama": nama, "deskripsi": deskripsi}
            )

        self.info = ""
        if info:
            info = info.text.strip()
            if not any(info == k["kode"] for k in self.kelas):
                self.info = info

    def _init_contoh(self, makna_label):
        indeks = makna_label.text.find(": ")
        if indeks != -1:
            contoh = makna_label.text[indeks + 2 :].strip()
            self.contoh = contoh.split("; ")
        else:
            self.contoh = []

    def serialisasi(self):
        return {
            "kelas": self.kelas,
            "submakna": self.submakna,
            "info": self.info,
            "contoh": self.contoh,
        }

    def _kelas(self):
        return " ".join(f"({k['kode']})" for k in self.kelas)

    def _submakna(self):
        return "; ".join(self.submakna)

    def _contoh(self):
        return "; ".join(self.contoh)

    def __str__(self, contoh=True):
        hasil = f"{self._kelas()}  " if self.kelas else ""
        hasil += self._submakna()
        hasil += f" {self.info}" if self.info else ""
        hasil += f": {self._contoh()}" if contoh and self.contoh else ""
        return hasil

    def __repr__(self):
        return f"<Makna: {'; '.join(self.submakna)}>"


class Etimologi:
    """Sebuah etimologi dalam sebuah entri KBBI daring."""

    def __init__(self, etimologi_html):
        """Membuat objek Etimologi baru berdasarkan etimologi_html yang diberikan.

        :param etimologi_html: String untuk etimologi yang ingin diproses.
        :type etimologi_html: str
        """
        if etimologi_html.startswith('['):
            etimologi_html = etimologi_html[1:-1]
        self.etimologi_data = BeautifulSoup(etimologi_html, 'html.parser')

        self._init_kelas()
        self._init_kata()
        self.arti = self.etimologi_data.text.strip()
        self.arti = self.arti.lstrip(
            "\'"
        ).rstrip(
            "\'"
        ).lstrip(
            "\""
        ).rstrip(
            "\""
        )

    def _init_kelas(self):
        bahasa = self.etimologi_data.find('i', {"style": "color:darkred"}).extract()
        kelas_d = []
        while True:
            kelas = self.etimologi_data.find('span', {"style": "color:red"})
            if not kelas:
                break
            kelas = self.etimologi_data.find('span', {"style": "color:red"}).extract()
            kelas_d.append(kelas.text.strip())
        self.kelas = kelas_d
        self.bahasa = bahasa.text.strip()

    def _init_kata(self):
        asal = self.etimologi_data.find('b').extract()
        lafal = self.etimologi_data.find('span', {"style": "color:darkgreen"}).extract()
        self.asal = asal.text.strip()
        self.pelafalan = lafal.text.strip()

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek Etimologi ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """

        return {
            "kelas": self.kelas,
            "bahasa": self.bahasa,
            "asal_kata": self.asal,
            "pelafalan": self.pelafalan,
            "arti": self.arti
        }

    def _kelas(self):
        """Mengembalikan representasi string untuk semua kelas kata makna ini.

        :returns: String representasi semua kelas kata
        :rtype: str
        """
        return " ".join(f"<{k}>" for k in self.kelas)

    def _asal_kata(self):
        """Mengembalikan representasi string untuk asal kata etimologi ini.

        :returns: String representasi asal kata
        :rtype: str
        """
        hasil = ""
        if self.asal:
            hasil += f"{self.asal} "
        if self.pelafalan:
            hasil += f"({self.pelafalan})"
        return hasil

    def __str__(self):
        hasil = f"[{self.bahasa}] " if self.bahasa else ""
        hasil += f"{self._kelas()} » " if self.kelas else ""
        hasil += self._asal_kata()
        hasil += f": {self.arti}" if self.arti else ""
        return hasil

    def __repr__(self):
        return f"<Etimologi: {self.arti}>"


def ambil_teks_dalam_label(sup, ambil_italic=False):
    """Mengambil semua teks dalam sup label HTML (tanpa anak-anaknya).

    :param sup: BeautifulSoup/Tag dari suatu label HTML
    :type sup: BeautifulSoup/Tag
    :returns: String semua teks dalam sup label HTML
    :rtype: str
    """
    if ambil_italic:
        italic = sup.find("i")
        if italic:
            sup = italic
    return "".join(i.strip() for i in sup.find_all(text=True, recursive=False))


class TidakDitemukan(Exception):
    """
    Galat yang menunjukkan bahwa laman tidak ditemukan dalam KBBI.
    """

    def __init__(self, kueri):
        super().__init__(f"{kueri} tidak ditemukan dalam KBBI!")


class TerjadiKesalahan(Exception):
    """
    Galat yang menunjukkan bahwa terjadi kesalahan dari pihak KBBI.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/Error
    """

    def __init__(self):
        super().__init__("Terjadi kesalahan saat memproses permintaan Anda.")


class BatasSehari(Exception):
    """
    Galat yang menunjukkan bahwa pencarian telah mencapai
    batas maksimum dalam sehari.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/BatasSehari
    """

    def __init__(self):
        super().__init__(
            "Pencarian Anda telah mencapai batas maksimum dalam sehari."
        )


class GagalAutentikasi(Exception):
    """
    Galat ketika gagal dalam autentikasi dengan KBBI.
    """

    def __init__(self):
        super().__init__('Gagal autentikasi dengan alamat surel dan sandi yang diberikan.')


def _parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "laman", help='Laman yang ingin diambil, contoh: "cinta"'
    )
    parser.add_argument(
        "-t",
        "--tanpa-contoh",
        help="jangan tampilkan contoh (bila ada)",
        action="store_true",
    )
    parser.add_argument(
        "-j",
        "--json",
        help="tampilkan hasil (selalu dengan contoh) dalam bentuk JSON",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--indentasi",
        help="gunakan indentasi sebanyak N untuk serialisasi JSON",
        type=int,
        metavar="N",
    )
    parser.add_argument(
        "-U",
        "--username",
        help="gunakan indentasi sebanyak N untuk serialisasi JSON",
        default=None,
        metavar="surel",
    )
    parser.add_argument(
        "-P",
        "--password",
        help="gunakan indentasi sebanyak N untuk serialisasi JSON",
        default=None,
        metavar="sandi",
    )
    return parser.parse_args(args)


def _keluaran(laman, args):
    if args.json:
        return json.dumps(laman.serialisasi(), indent=args.indentasi)
    else:
        return laman.__str__(contoh=not args.tanpa_contoh)


def main(argv=None):
    """Program utama dengan CLI."""
    if argv is None:
        argv = sys.argv[1:]
    args = _parse_args(argv)
    try:
        laman = KBBI(args.laman, email=args.username, password=args.password)
    except (TidakDitemukan, TerjadiKesalahan, BatasSehari) as e:
        print(e)
        return 1
    else:
        print(_keluaran(laman, args))
        return 0


if __name__ == "__main__":
    sys.exit(main())
