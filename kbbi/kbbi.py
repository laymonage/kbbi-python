"""
:mod:`kbbi` -- Modul KBBI Python
================================

.. module:: kbbi
   :platform: Unix, Windows, Mac
   :synopsis: Modul ini mengandung implementasi dari modul kbbi.
.. moduleauthor:: sage <laymonage@gmail.com>
"""

from re import sub
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


class KBBI:
    """Sebuah laman dalam KBBI daring."""
    host = "https://kbbi.kemdikbud.go.id"

    class TidakDitemukan(Exception):
        """
        Galat yang menunjukkan bahwa laman tidak ditemukan dalam KBBI.
        """

        def __init__(self, kata_kunci):
            super().__init__(f"{kata_kunci} tidak ditemukan dalam KBBI!")

    class TerjadiKesalahan(Exception):
        """
        Galat yang menunjukkan bahwa terjadi kesalahan dari pihak KBBI.
        Laman: https://kbbi.kemdikbud.go.id/Beranda/Error
        """

        def __init__(self):
            super().__init__('Terjadi kesalahan saat memproses permintaan Anda.')

    def __init__(self, kata_kunci):
        """Membuat objek KBBI baru berdasarkan kata_kunci yang diberikan.

        :param kata_kunci: Kata kunci pencarian
        :type kata_kunci: str
        """
        kasus_khusus = [
            '.' in kata_kunci,
            '?' in kata_kunci,
            kata_kunci.lower() == 'nul',
            kata_kunci.lower() == 'bin',
        ]
        if any(kasus_khusus):
            url = f"{self.host}/Cari/Hasil?frasa={quote(kata_kunci)}"
        else:
            url = f"{self.host}/entri/{quote(kata_kunci)}"
        laman = requests.get(url)

        if "Beranda/Error" in laman.url:
            raise self.TerjadiKesalahan()

        if "Entri tidak ditemukan." in laman.text:
            raise self.TidakDitemukan(kata_kunci)

        self.nama = kata_kunci.lower()
        self.entri = []
        self._init_entri(laman)

    def _init_entri(self, laman):
        """Membuat objek-objek entri dari laman yang diambil.

        :param laman: Laman respons yang dikembalikan oleh KBBI daring.
        :type laman: Response
        """

        sup = BeautifulSoup(laman.text, "html.parser")
        estr = ""
        for label in sup.find("hr").next_siblings:
            if label.name == "hr":
                try:
                    label["style"]
                    continue
                except KeyError:
                    self.entri.append(Entri(estr))
                    break
            if label.name == "h2":
                try:
                    if label["style"] == "color:gray":
                        continue
                except KeyError:
                    pass
                if estr:
                    self.entri.append(Entri(estr))
                estr = ""
            estr += str(label).strip()

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek KBBI ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """

        return {self.nama: [entri.serialisasi() for entri in self.entri]}

    def __str__(self, contoh=True):
        result = "\n\n".join(str(entri) for entri in self.entri)
        if not contoh:
            result = sub(":.*--.*", "", result)
        return result

    def __repr__(self):
        return f"<KBBI: {self.nama}>"


class Entri:
    """Sebuah entri dalam sebuah laman KBBI daring."""

    def __init__(self, entri_html):
        """Membuat objek Entri baru berdasarkan entri_html yang diberikan.

        :param entri_html: String HTML untuk entri yang ingin diproses.
        :type entri_html: str
        """

        entri = BeautifulSoup(entri_html, "html.parser")
        judul = entri.find("h2")
        dasar = judul.find_all(class_="rootword")
        nomor = judul.find("sup", recursive=False)
        lafal = judul.find(class_="syllable")
        varian = judul.find("small")
        if entri.find(color="darkgreen"):
            makna = [entri]
        else:
            makna = entri.find_all("li")

        self.nama = ambil_teks_dalam_label(judul, ambil_italic=True)
        if not self.nama:
            self.nama = judul.find_all(text=True)[0].strip()
        self.nomor = nomor.text.strip() if nomor else ""
        self.kata_dasar = []
        self._init_kata_dasar(dasar)
        self.pelafalan = lafal.text.strip() if lafal else ""

        self.bentuk_tidak_baku = []
        self.varian = []
        if varian:
            bentuk_tidak_baku = varian.find_all("b")
            if bentuk_tidak_baku:
                self.bentuk_tidak_baku = "".join(
                    e.text.strip() for e in bentuk_tidak_baku
                ).split(", ")
            else:
                self.varian = varian.text[len("varian: ") :].strip().split(", ")

        self.makna = [Makna(m) for m in makna]

    def _init_kata_dasar(self, dasar):
        """Memproses kata dasar yang ada dalam nama entri.

        :param dasar: ResultSet untuk label HTML dengan class="rootword"
        :type dasar: ResultSet
        """

        for tiap in dasar:
            kata = tiap.find("a")
            dasar_no = kata.find("sup")
            kata = ambil_teks_dalam_label(kata)
            self.kata_dasar.append(
                f"{kata} [{dasar_no.text.strip()}]" if dasar_no else kata
            )

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek Entri ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """

        return {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "makna": [makna.serialisasi() for makna in self.makna],
        }

    def _makna(self):
        """Mengembalikan representasi string untuk semua makna entri ini.

        :returns: String representasi makna-makna
        :rtype: str
        """

        if len(self.makna) > 1:
            return "\n".join(f"{i}. {makna}" for i, makna in enumerate(self.makna, 1))
        if len(self.makna) == 1:
            return str(self.makna[0])
        return ""

    def _nama(self):
        """Mengembalikan representasi string untuk nama entri ini.

        :returns: String representasi nama entri
        :rtype: str
        """

        hasil = self.nama
        if self.nomor:
            hasil += f" [{self.nomor}]"
        if self.kata_dasar:
            hasil = f"{' » '.join(self.kata_dasar)} » {hasil}"
        return hasil

    def _varian(self, varian):
        """Mengembalikan representasi string untuk varian entri ini.
        Dapat digunakan untuk "Varian" maupun "Bentuk tidak baku".

        :param varian: List bentuk tidak baku atau varian
        :type varian: list
        :returns: String representasi varian atau bentuk tidak baku
        :rtype: str
        """

        if varian == self.bentuk_tidak_baku:
            nama = "Bentuk tidak baku"
        elif varian == self.varian:
            nama = "Varian"
        else:
            return ""
        return f"{nama}: {', '.join(varian)}"

    def __str__(self):
        hasil = self._nama()
        if self.pelafalan:
            hasil += f"  {self.pelafalan}"
        for var in (self.bentuk_tidak_baku, self.varian):
            if var:
                hasil += f"\n{self._varian(var)}"
        return f"{hasil}\n{self._makna()}"

    def __repr__(self):
        return f"<Entri: {self._nama()}>"


class Makna:
    """Sebuah makna dalam sebuah entri KBBI daring."""

    def __init__(self, makna_label):
        """Membuat objek Makna baru berdasarkan makna_label yang diberikan.

        :param makna_label: BeautifulSoup untuk makna yang ingin diproses.
        :type makna_label: BeautifulSoup
        """
        self.submakna = makna_label.get_text().strip()
        self.orig_submakna = self.submakna
        baku = makna_label.find("a")
        if baku:
            self.submakna = f"→ {ambil_teks_dalam_label(baku)}"
            nomor = baku.find("sup")
            if nomor:
                self.submakna += f" [{nomor.text.strip()}]"
        self._init_kelas(makna_label)
        self._init_contoh(makna_label)
        self._bersihkan_submakna()

    def _init_kelas(self, makna_label):
        """Memproses kelas kata yang ada dalam makna.

        :param makna_label: BeautifulSoup untuk makna yang ingin diproses.
        :type makna_label: BeautifulSoup
        """

        kelas = makna_label.find(color="red")
        lain = makna_label.find(color="darkgreen")
        info = makna_label.find(color="green")
        if kelas:
            kelas = kelas.find_all("span")
        if lain:
            self.kelas = {lain.text.strip(): lain["title"].strip()}
            self.submakna = lain.next_sibling.strip()
            self.submakna += f" {makna_label.find(color='grey').get_text().strip()}"
        else:
            self.kelas = (
                {k.text.strip(): k["title"].strip() for k in kelas} if kelas else {}
            )
        self.info = info.text.strip() if info else ""

    def _init_contoh(self, makna_label):
        """Memproses contoh yang ada dalam makna.

        :param makna_label: BeautifulSoup untuk makna yang ingin diproses.
        :type makna_label: BeautifulSoup
        """

        indeks = makna_label.text.find(": ")
        if indeks != -1:
            contoh = makna_label.text[indeks + 2 :].strip()
            self.contoh = contoh.split("; ")
        else:
            self.contoh = []

    def _bersihkan_submakna(self):
        """Membersihkan hasil submakna dari teks kelas dan contoh"""
        if self.submakna == self.orig_submakna:
            for k in self.kelas:
                if self.submakna.find(k) != -1:
                    self.submakna = self.submakna[len(k)+1:]

            indeks = self.submakna.find(': ')
            if indeks != -1:
                self.submakna = self.submakna[:indeks]

            if self.info:
                self.submakna = self.submakna[
                    :self.submakna.find(self.info)
                ]
            self.submakna = self.submakna.rstrip(':')
        self.submakna = self.submakna.split('; ')

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek Makna ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """

        return {
            "kelas": self.kelas,
            "submakna": self.submakna,
            "info": self.info,
            "contoh": self.contoh,
        }

    def _kelas(self):
        """Mengembalikan representasi string untuk semua kelas kata makna ini.

        :returns: String representasi semua kelas kata
        :rtype: str
        """
        return " ".join(f"({k})" for k in self.kelas)

    def _submakna(self):
        """Mengembalikan representasi string untuk semua submakna makna ini.

        :returns: String representasi semua submakna
        :rtype: str
        """
        return "; ".join(self.submakna)

    def _contoh(self):
        """Mengembalikan representasi string untuk semua contoh makna ini.

        :returns: String representasi semua contoh
        :rtype: str
        """
        return "; ".join(self.contoh)

    def __str__(self):
        hasil = f"{self._kelas()}  " if self.kelas else ""
        hasil += self._submakna()
        hasil += f" {self.info}" if self.info else ""
        hasil += f": {self._contoh()}" if self.contoh else ""
        return hasil

    def __repr__(self):
        return f"<Makna: {'; '.join(self.submakna)}>"


def ambil_teks_dalam_label(sup, ambil_italic=False):
    """Mengambil semua teks dalam sup label HTML (tanpa anak-anaknya).

    :param sup: BeautifulSoup dari suatu label HTML
    :type sup: BeautifulSoup
    :returns: String semua teks dalam sup label HTML
    :rtype: str
    """
    if ambil_italic:
        italic = sup.find('i')
        if italic:
            sup = italic
    return "".join(i.strip() for i in sup.find_all(text=True, recursive=False))
