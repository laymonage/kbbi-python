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
import re
import sys
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


class KBBI:
    """Sebuah laman dalam KBBI daring."""

    host = "https://kbbi.kemdikbud.go.id"

    def __init__(self, kueri, auth=None):
        """Membuat objek KBBI baru berdasarkan kueri yang diberikan.

        :param kueri: Kata kunci pencarian
        :type kueri: str
        :param auth: objek AutentikasiKBBI
        :type auth: AutentikasiKBBI
        """
        self.nama = kueri
        self._init_pranala()
        if auth is not None:
            if not isinstance(auth, AutentikasiKBBI):
                raise ValueError(
                    'KBBI: "auth" harus merupakan objek AutentikasiKBBI'
                )
            self.sesi = auth.ambil_sesi()
        else:
            self.sesi = requests.Session()
        laman = self.sesi.get(self.pranala)
        self._cek_autentikasi(laman)
        self._cek_galat(laman)
        self._init_entri(laman)

    def _cek_autentikasi(self, laman):
        self.terautentikasi = "loginLink" not in laman.text

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

    def _init_entri(self, laman):
        sup = BeautifulSoup(laman.text, "html.parser")
        estr = ""
        self.entri = []
        for label in sup.find("hr").next_siblings:
            if label.name == "hr":
                if label.get("style") is None:
                    self.entri.append(Entri(estr, self.terautentikasi))
                    break
                else:
                    continue
            if label.name == "h2":
                if label.get("style") == "color:gray":
                    continue
                if estr:
                    self.entri.append(Entri(estr, self.terautentikasi))
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

    def __init__(self, entri_html, terautentikasi=False):
        entri = BeautifulSoup(entri_html, "html.parser")
        judul = entri.find("h2")
        self.terautentikasi = terautentikasi
        self._init_nama(judul)
        self._init_nomor(judul)
        self._init_kata_dasar(judul)
        self._init_pelafalan(judul)
        self._init_varian(judul)
        self._init_terkait(entri)
        self._init_etimologi(entri)
        self._init_makna(entri)

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
            variasi = judul.find_all("small")
            varian = None
            for v in variasi:
                spanv = v.find("span")
                if spanv and "entrisButton" in spanv.get("class", []):
                    continue
                varian = v
        else:
            varian = judul.find("small")
        self.bentuk_tidak_baku = []
        self.varian = []
        if varian is None:
            return
        bentuk_tidak_baku = varian.find_all("b")
        if bentuk_tidak_baku:
            self.bentuk_tidak_baku = "".join(
                e.text.strip() for e in bentuk_tidak_baku
            ).split(", ")
        else:
            self.varian = varian.text[len("varian: ") :].strip().split(", ")

    def _init_etimologi(self, entri):
        self.etimologi = None
        if not self.terautentikasi:
            return
        etimologi = entri.find(text="Etimologi:")
        if etimologi is None:
            return
        etimologi = etimologi.parent
        etistr = ""
        for eti in etimologi.next_siblings:
            if eti.name == "br":
                break
            etistr += str(eti).strip()
        self.etimologi = Etimologi(etistr)

    def _init_terkait(self, entri):
        self.terkait = {
            "kata_turunan": [],
            "gabungan_kata": [],
            "peribahasa": [],
            "kiasan": [],
        }
        if not self.terautentikasi:
            return
        terkait = entri.find_all("h4")
        for le in terkait:
            if not le:
                continue
            le_txt = le.text.strip()
            for jenis in self.terkait:
                if jenis.replace("_", " ").title() in le_txt:
                    kumpulan = le.next_sibling
                    if kumpulan:
                        kumpulan = kumpulan.find_all("a")
                        self.terkait[jenis] = [k.text for k in kumpulan if k]

    def _init_makna(self, entri):
        prakategorial = entri.find(color="darkgreen")
        if prakategorial:
            makna = [prakategorial]
        else:
            makna = entri.find_all("li")
        if self.terautentikasi and not prakategorial:
            makna = [
                m for m in makna if m and "Usulkan makna baru" not in m.text
            ]
            terkait = sum([bool(t) for t in self.terkait.values()])
            if terkait:
                makna = makna[:-terkait]
        self.makna = [Makna(m) for m in makna]

    def serialisasi(self):
        entri = {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "makna": [makna.serialisasi() for makna in self.makna],
        }
        if self.terautentikasi:
            if self.etimologi is not None:
                entri.update({"etimologi": self.etimologi.serialisasi()})
            else:
                entri.update({"etimologi": None})
            entri.update(self.terkait)
        return entri

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

    def _terkait(self):
        nama_murni = self.nama.replace(".", "")
        hasil = ""
        header = {
            "kata_turunan": "\nKata Turunan",
            "gabungan_kata": "\nGabungan Kata",
            "peribahasa": f"\nPeribahasa (mengandung [{nama_murni}])",
            "kiasan": f"\nKiasan (mengandung [{nama_murni}])",
        }
        for key, head in header.items():
            if self.terkait[key]:
                hasil += f"{head}\n{'; '.join(self.terkait[key])}"
        return hasil

    def __str__(self, contoh=True):
        hasil = self._nama()
        if self.pelafalan:
            hasil += f"  {self.pelafalan}"
        for var in (self.bentuk_tidak_baku, self.varian):
            if var:
                hasil += f"\n{self._varian(var)}"
        if self.terautentikasi and self.etimologi:
            hasil += f"\nEtimologi: {self.etimologi}"
        if self.makna:
            hasil += f"\n{self._makna(contoh)}"
        if self.terautentikasi:
            hasil += self._terkait()
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

    def _init_prakategorial(self, prakategorial):
        cari = prakategorial.next_sibling
        self.submakna = cari.strip()
        self.submakna += f" {cari.next_sibling.text.strip()}"

    def _init_rujukan(self, rujukan):
        self.submakna = f"→ {ambil_teks_dalam_label(rujukan)}"
        nomor = rujukan.find("sup")
        if nomor:
            self.submakna += f" ({nomor.text.strip()})"

    def _init_submakna(self, makna_label):
        rujukan = makna_label.find("a")
        if rujukan:
            self._init_rujukan(rujukan)
        elif makna_label.get("color") == "darkgreen":
            self._init_prakategorial(makna_label)
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
        info = makna_label.find(color="green")

        if kelas:
            kelas = kelas.find_all("span")
        if makna_label.get("color") == "darkgreen":  # prakategorial
            kelas = [makna_label]

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
        etimologi_html = etimologi_html.lstrip("[").rstrip("]")
        etimologi = BeautifulSoup(etimologi_html, "html.parser")
        self._init_bahasa(etimologi)
        self._init_kelas(etimologi)
        self._init_asal_kata(etimologi)
        self._init_pelafalan(etimologi)
        self._init_arti(etimologi)

    def _init_bahasa(self, etimologi):
        bahasa = etimologi.find("i", style="color:darkred")
        self.bahasa = ekstraksi_aman(bahasa)

    def _init_kelas(self, etimologi):
        kelas = etimologi.find_all("span", style="color:red")
        self.kelas = [ekstraksi_aman(k) for k in kelas]

    def _init_asal_kata(self, etimologi):
        asal = etimologi.find("b")
        self.asal_kata = ekstraksi_aman(asal)

    def _init_pelafalan(self, etimologi):
        lafal = etimologi.find("span", style="color:darkgreen")
        self.pelafalan = ekstraksi_aman(lafal)

    def _init_arti(self, etimologi):
        self.arti = etimologi.text.strip().strip("'\"").split("; ")

    def serialisasi(self):
        """Mengembalikan hasil serialisasi objek Etimologi ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """

        return {
            "kelas": self.kelas,
            "bahasa": self.bahasa,
            "asal_kata": self.asal_kata,
            "pelafalan": self.pelafalan,
            "arti": self.arti,
        }

    def _kelas(self):
        """Mengembalikan representasi string untuk semua kelas kata makna ini.

        :returns: String representasi semua kelas kata
        :rtype: str
        """
        return " ".join(f"({k})" for k in self.kelas)

    def _asal_kata(self):
        """Mengembalikan representasi string untuk asal kata etimologi ini.

        :returns: String representasi asal kata
        :rtype: str
        """
        return " ".join((self.asal_kata, self.pelafalan))

    def _arti(self):
        return "; ".join(self.arti)

    def __str__(self):
        hasil = f"[{self.bahasa}]" if self.bahasa else ""
        hasil += f" {self._kelas()}" if self.kelas else ""
        if self.asal_kata or self.pelafalan:
            hasil += f"  {self._asal_kata()}"
        hasil += f": {self._arti()}" if self.arti else ""
        return hasil

    def __repr__(self):
        return f"<Etimologi: {self.asal_kata}>"


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


def ekstraksi_aman(sup):
    """Mengekstraksi sup dan mengembalikan .text.strip()-nya secara aman."""
    if sup:
        return sup.extract().text.strip()
    return ""


class AutentikasiKBBI:
    """Gunakan fitur pengguna terdaftar."""

    host = "https://kbbi.kemdikbud.go.id"

    def __init__(self, posel=None, sandi=None):
        """Melakukan autentikasi dengan alamat posel dan sandi yang diberikan.
        Objek AutentikasiKBBI dapat digunakan dalam pembuatan objek KBBI
        untuk mendapatkan fitur pengguna terdaftar.

        Jika posel dan sandi tidak diberikan, autentikasi akan menggunakan kuki
        yang tersimpan (jika ada).

        :param posel: Alamat posel yang terdaftar di KBBI Daring
        :type email: str
        :param sandi: Kata sandi untuk akun dengan alamat surel yang diberikan
        :type sandi: str
        """
        self.sesi = requests.Session()
        if posel is None and sandi is None:
            self.__ambil_kuki()
        else:
            self._autentikasi(posel, sandi)

    def simpan_kuki(self):
        self.__simpan_kuki()

    def __simpan_kuki(self):
        save_folder = Path(f"{str(Path.home())}/.config/kbbi_data")
        if not save_folder.exists():
            save_folder.mkdir()
        aspcookie = self.sesi.cookies.get(".AspNet.ApplicationCookie")
        save_folder.joinpath("kuki.txt").write_text(
            f".AspNet.ApplicationCookie={aspcookie};"
        )

    def __ambil_kuki(self):
        save_folder = Path(f"{str(Path.home())}/.config/kbbi_data")
        if not save_folder.exists():
            return
        if save_folder.joinpath("kuki.txt").exists():
            self.sesi.headers.update(
                {"Cookie": save_folder.joinpath("kuki.txt").read_text()}
            )

    def _autentikasi(self, posel, sandi):
        laman = self.sesi.get(f"{self.host}/Account/Login")
        token = re.findall(
            r"<input name=\"__RequestVerificationToken\".*value=\"(.*)\" />",
            laman.text,
        )
        if not token:
            raise TerjadiKesalahan()
        payload = {
            "__RequestVerificationToken": token[0],
            "Posel": posel,
            "KataSandi": sandi,
            "IngatSaya": True,
        }
        laman = self.sesi.post(f"{self.host}/Account/Login", data=payload)
        if "Beranda/Error" in laman.url:
            raise TerjadiKesalahan()
        if "Account/Login" in laman.url:
            raise GagalAutentikasi()

    def ambil_sesi(self):
        """Mengembalikan sesi yang telah dibuat.

        :returns: sesi dengan fitur pengguna terdaftar
        :rtype: requests.Session
        """
        return self.sesi


class Galat(Exception):
    pass


class TidakDitemukan(Galat):
    """
    Galat yang menunjukkan bahwa laman tidak ditemukan dalam KBBI.
    """

    def __init__(self, kueri):
        super().__init__(f"{kueri} tidak ditemukan dalam KBBI!")


class TerjadiKesalahan(Galat):
    """
    Galat yang menunjukkan bahwa terjadi kesalahan dari pihak KBBI.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/Error
    """

    def __init__(self):
        super().__init__("Terjadi kesalahan saat memproses permintaan Anda.")


class BatasSehari(Galat):
    """
    Galat yang menunjukkan bahwa pencarian telah mencapai
    batas maksimum dalam sehari.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/BatasSehari
    """

    def __init__(self):
        super().__init__(
            "Pencarian Anda telah mencapai batas maksimum dalam sehari."
        )


class GagalAutentikasi(Galat):
    """
    Galat ketika gagal dalam autentikasi dengan KBBI.
    """

    def __init__(self):
        super().__init__(
            "Gagal melakukan autentikasi dengan alamat surel dan sandi "
            "yang diberikan."
        )


def _parse_args_autentikasi(args):
    parser = argparse.ArgumentParser(
        description=(
            "Melakukan autentikasi dengan alamat posel dan sandi "
            "yang diberikan."
        ),
        epilog=(
            "Setelah autentikasi berhasil, kuki akan disimpan dan "
            "otomatis digunakan dalam penggunaan KBBI berikutnya."
        ),
    )
    parser.add_argument(
        "posel", help="alamat posel (pos elektronik) akun KBBI Daring"
    )
    parser.add_argument(
        "sandi", help="kata sandi akun KBBI Daring dengan posel yang diberikan"
    )
    return parser.parse_args(args)


def autentikasi(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = _parse_args_autentikasi(argv)
    try:
        auth = AutentikasiKBBI(args.posel, args.sandi)
    except Galat as e:
        print(e)
        return 1
    else:
        auth.simpan_kuki()
        print(
            "Autentikasi berhasil dan kuki telah disimpan.\n"
            "Kuki akan otomatis digunakan pada penggunaan KBBI berikutnya."
        )
    return 0


def _parse_args_utama(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "laman", help='laman yang ingin diambil, contoh: "cinta"'
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
    args = _parse_args_utama(argv)
    try:
        laman = KBBI(args.laman, AutentikasiKBBI())
    except Galat as e:
        print(e)
        return 1
    else:
        print(_keluaran(laman, args))
        return 0


if __name__ == "__main__":
    sys.exit(main())
