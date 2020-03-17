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
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


class KBBI:
    """Sebuah laman dalam KBBI daring."""

    host = "https://kbbi.kemdikbud.go.id"

    def __init__(self, kata_kunci):
        """Membuat objek KBBI baru berdasarkan kata_kunci yang diberikan.

        :param kata_kunci: Kata kunci pencarian
        :type kata_kunci: str
        """
        kasus_khusus = [
            "." in kata_kunci,
            "?" in kata_kunci,
            kata_kunci.lower() == "nul",
            kata_kunci.lower() == "bin",
        ]
        if any(kasus_khusus):
            self.pranala = f"{self.host}/Cari/Hasil?frasa={quote(kata_kunci)}"
        else:
            self.pranala = f"{self.host}/entri/{quote(kata_kunci)}"
        laman = requests.get(self.pranala)

        if "Beranda/Error" in laman.url:
            raise TerjadiKesalahan()
        if "Beranda/BatasSehari" in laman.url:
            raise BatasSehari()
        if "Entri tidak ditemukan." in laman.text:
            raise TidakDitemukan(kata_kunci)

        self.nama = kata_kunci.lower()
        self.entri = []
        self._init_entri(laman)

    def _init_entri(self, laman):
        sup = BeautifulSoup(laman.text, "html.parser")
        estr = ""
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
                self.varian = (
                    varian.text[len("varian: ") :].strip().split(", ")
                )

        self.makna = [Makna(m) for m in makna]

    def _init_kata_dasar(self, dasar):
        for tiap in dasar:
            kata = tiap.find("a")
            dasar_no = kata.find("sup")
            kata = ambil_teks_dalam_label(kata)
            self.kata_dasar.append(
                f"{kata} ({dasar_no.text.strip()})" if dasar_no else kata
            )

    def serialisasi(self):
        return {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "makna": [makna.serialisasi() for makna in self.makna],
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
            nama = "Bentuk tidak baku"
        elif varian == self.varian:
            nama = "Varian"
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
        return f"{hasil}\n{self._makna(contoh)}"

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

    def __init__(self, kata_kunci):
        super().__init__(f"{kata_kunci} tidak ditemukan dalam KBBI!")


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
        laman = KBBI(args.laman)
    except (TidakDitemukan, TerjadiKesalahan, BatasSehari) as e:
        print(e)
    else:
        print(_keluaran(laman, args))


if __name__ == "__main__":
    main()
