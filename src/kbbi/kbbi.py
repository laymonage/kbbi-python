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
from appdirs import AppDirs
from bs4 import BeautifulSoup

APPDIR = AppDirs("kbbi", "laymonage")
CONFIG_DIR = Path(APPDIR.user_config_dir)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


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
        self._init_lokasi()
        self._init_sesi(auth)
        laman = self.sesi.get(f"{self.host}/{self.lokasi}")
        self._cek_autentikasi(laman)
        self._cek_galat(laman)
        self._init_entri(laman)

    def _init_sesi(self, auth):
        if auth is not None:
            if not isinstance(auth, AutentikasiKBBI):
                raise ValueError("'auth' harus berupa objek AutentikasiKBBI.")
            self.sesi = auth.sesi
        else:
            self.sesi = requests.Session()

    def _cek_autentikasi(self, laman):
        self.terautentikasi = "loginLink" not in laman.text

    def _init_lokasi(self):
        kasus_khusus = [
            "." in self.nama,
            "?" in self.nama,
            self.nama.lower() == "nul",
            self.nama.lower() == "bin",
        ]
        if any(kasus_khusus):
            self.lokasi = f"Cari/Hasil?frasa={quote(self.nama)}"
        else:
            self.lokasi = f"entri/{quote(self.nama)}"

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
        label = sup.find("hr").next_sibling
        while not (label.name == "hr" and label.get("style") is None):
            if label.name == "h2":
                if label.get("style") == "color:gray":  # Lampiran
                    label = label.next_sibling
                    continue
                if estr:
                    self.entri.append(Entri(estr, self.terautentikasi))
                    estr = ""
            estr += str(label).strip()
            label = label.next_sibling
        self.entri.append(Entri(estr, self.terautentikasi))

    def serialisasi(self, fitur_pengguna=True):
        """Mengembalikan hasil serialisasi objek KBBI ini.

        :returns: Dictionary hasil serialisasi
        :rtype: dict
        """
        return {
            "pranala": f"{self.host}/{self.lokasi}",
            "entri": [
                entri.serialisasi(fitur_pengguna) for entri in self.entri
            ],
        }

    def __str__(self, contoh=True, terkait=True, fitur_pengguna=True):
        return "\n\n".join(
            entri.__str__(contoh, terkait, fitur_pengguna)
            for entri in self.entri
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
            for b in bentuk_tidak_baku:
                nama = b.find(text=True).strip().lstrip(", ")
                nomor = b.find("sup")
                if nomor:
                    nama = f"{nama} ({nomor.text.strip()})"
                self.bentuk_tidak_baku.append(nama)
        else:
            self.varian = varian.text[len("varian: ") :].strip().split(", ")

    def _init_etimologi(self, entri):
        self.etimologi = None
        if not self.terautentikasi:
            return
        etimologi = entri.find(text="Etimologi:")
        if etimologi is None:
            return
        etimologi = etimologi.parent.next_sibling
        etistr = ""
        while etimologi.name != "br":
            etistr += str(etimologi).strip()
            etimologi = etimologi.next_sibling
        self.etimologi = Etimologi(etistr)

    def _init_terkait(self, entri):
        if not self.terautentikasi:
            self.terkait = None
            return
        self.terkait = {
            "kata_turunan": [],
            "gabungan_kata": [],
            "peribahasa": [],
            "kiasan": [],
        }
        terkait = entri.find_all("h4")
        for le in terkait:
            le_txt = le.text.strip()
            for jenis in self.terkait:
                if jenis.replace("_", " ").title() in le_txt:
                    kumpulan = le.next_sibling
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

    def serialisasi(self, fitur_pengguna=True):
        entri = {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "makna": [makna.serialisasi() for makna in self.makna],
        }
        if self.terautentikasi and fitur_pengguna:
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
        return self.makna[0].__str__(contoh=contoh)

    def _nama(self):
        hasil = self.nama
        if self.nomor:
            hasil += f" ({self.nomor})"
        if self.kata_dasar:
            hasil = f"{' » '.join(self.kata_dasar)} » {hasil}"
        return hasil

    def _varian(self):
        if self.bentuk_tidak_baku:
            return f"bentuk tidak baku: {', '.join(self.bentuk_tidak_baku)}"
        elif self.varian:
            return f"varian: {', '.join(self.varian)}"
        return ""

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

    def __str__(self, contoh=True, terkait=True, fitur_pengguna=True):
        hasil = self._nama()
        if self.pelafalan:
            hasil += f"  {self.pelafalan}"
        varian = self._varian()
        if varian:
            hasil += f"\n{varian}"
        if self.terautentikasi and fitur_pengguna and self.etimologi:
            hasil += f"\nEtimologi: {self.etimologi}"
        if self.makna:
            hasil += f"\n{self._makna(contoh)}"
        if self.terautentikasi and fitur_pengguna and terkait:
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
        entris = makna_label.find("span", class_="entrisButton")
        if entris:
            entris.extract()
        if rujukan and not rujukan.find("span", style="color:red"):
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
        return f"<Makna: {self._submakna()}>"


class Etimologi:
    """Sebuah etimologi dalam sebuah entri KBBI daring."""

    def __init__(self, etimologi_html):
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
        return {
            "kelas": self.kelas,
            "bahasa": self.bahasa,
            "asal_kata": self.asal_kata,
            "pelafalan": self.pelafalan,
            "arti": self.arti,
        }

    def _kelas(self):
        return " ".join(f"({k})" for k in self.kelas)

    def _asal_kata(self):
        return " ".join((self.asal_kata, self.pelafalan))

    def _arti(self):
        return "; ".join(self.arti)

    def __str__(self):
        hasil = f"[{self.bahasa}]" if self.bahasa else ""
        hasil += f" {self._kelas()}" if self.kelas else ""
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
    lokasi = "Account/Login"
    lokasi_kuki = CONFIG_DIR / "kuki.json"

    def __init__(self, posel=None, sandi=None, lokasi_kuki=None):
        """Melakukan autentikasi dengan alamat posel dan sandi yang diberikan.
        Objek AutentikasiKBBI dapat digunakan dalam pembuatan objek KBBI
        untuk mendapatkan fitur pengguna terdaftar.

        Jika posel dan sandi tidak diberikan, autentikasi akan menggunakan kuki
        yang tersimpan (jika ada).

        :param posel: Alamat posel yang terdaftar di KBBI Daring
        :type email: str
        :param sandi: Kata sandi untuk akun dengan alamat posel yang diberikan
        :type sandi: str
        :param lokasi_kuki: Lokasi kuki yang akan dimuat/disimpan
        :type lokasi_kuki: str atau PathLike
        """
        self.sesi = requests.Session()
        self.lokasi_kuki = lokasi_kuki or self.lokasi_kuki
        if posel is None and sandi is None:
            try:
                self.ambil_kuki()
            except FileNotFoundError as e:
                raise KukiTidakDitemukan(self.lokasi_kuki) from e
        else:
            token = self._ambil_token()
            self._autentikasi(posel, sandi, token)

    def simpan_kuki(self):
        kuki_aspnet = self.sesi.cookies.get(".AspNet.ApplicationCookie")
        kuki_sesi = {".AspNet.ApplicationCookie": kuki_aspnet}
        with open(self.lokasi_kuki, "w") as kuki:
            json.dump(kuki_sesi, kuki)

    def ambil_kuki(self):
        with open(self.lokasi_kuki) as kuki:
            self.sesi.cookies.update(json.load(kuki))

    def _ambil_token(self):
        laman = self.sesi.get(f"{self.host}/{self.lokasi}")
        token = re.search(
            r"<input name=\"__RequestVerificationToken\".*value=\"(.*)\" />",
            laman.text,
        )
        if not token:
            raise TerjadiKesalahan()
        return token.group(1)

    def _autentikasi(self, posel, sandi, token):
        payload = {
            "__RequestVerificationToken": token,
            "Posel": posel,
            "KataSandi": sandi,
            "IngatSaya": True,
        }
        laman = self.sesi.post(f"{self.host}/{self.lokasi}", data=payload)
        if "Beranda/Error" in laman.url:
            raise TerjadiKesalahan()
        if "Account/Login" in laman.url:
            raise GagalAutentikasi()


class Galat(Exception):
    pass


class TidakDitemukan(Galat):
    """Galat ketika laman tidak ditemukan dalam KBBI."""

    def __init__(self, kueri):
        super().__init__(f"{kueri} tidak ditemukan dalam KBBI.")


class TerjadiKesalahan(Galat):
    """Galat ketika terjadi kesalahan dari pihak KBBI.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/Error
    """

    def __init__(self):
        super().__init__("Terjadi kesalahan saat memproses permintaan Anda.")


class BatasSehari(Galat):
    """Galat ketika pencarian telah mencapai batas maksimum dalam sehari.
    Laman: https://kbbi.kemdikbud.go.id/Beranda/BatasSehari
    """

    def __init__(self):
        super().__init__(
            "Pencarian Anda telah mencapai batas maksimum dalam sehari."
        )


class GagalAutentikasi(Galat):
    """Galat ketika gagal melakukan autentikasi dengan KBBI."""

    def __init__(self, pesan=None):
        super().__init__(
            pesan
            or "Gagal melakukan autentikasi dengan alamat posel dan sandi "
            "yang diberikan."
        )


class KukiTidakDitemukan(GagalAutentikasi):
    """Galat ketika lokasi kuki yang diberikan tidak ditemukan."""

    def __init__(self, lokasi_kuki, posel_sandi=True):
        if posel_sandi:
            super().__init__(
                f"Posel dan sandi tidak diberikan, "
                f"tetapi kuki tidak ditemukan pada {lokasi_kuki}"
            )
        else:
            super().__init__(f"Kuki tidak ditemukan pada {lokasi_kuki}!")


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
        add_help=False,
    )
    parser.add_argument(
        "posel",
        help="alamat posel (pos elektronik) akun KBBI Daring",
        nargs="?",
    )
    parser.add_argument(
        "sandi",
        help="kata sandi akun KBBI Daring dengan posel yang diberikan",
        nargs="?",
    )
    parser.add_argument(
        "--lokasi-kuki",
        "-l",
        help="lokasi menuju berkas kuki yang akan disimpan",
        metavar="LOKASI",
    )
    parser.add_argument(
        "-h",
        "-b",
        "--help",
        "--bantuan",
        action="store_true",
        dest="bantuan",
        help="tampilkan pesan bantuan ini dan keluar",
    )
    parser.add_argument(
        "-c",
        "--bersihkan",
        help="bersihkan kuki yang tersimpan",
        action="store_true",
    )
    return parser.parse_args(args), parser


def _bersihkan_kuki(lokasi_kuki):
    try:
        lokasi_kuki.unlink()
    except FileNotFoundError:
        print(KukiTidakDitemukan(lokasi_kuki, posel_sandi=False))
        return 1
    else:
        print(f"Kuki {lokasi_kuki} berhasil dihapus.")
        return 0


def autentikasi(argv=None):
    """Program CLI untuk autentikasi."""
    if argv is None:
        argv = sys.argv[1:]
    args, parser = _parse_args_autentikasi(argv)
    lokasi_kuki = AutentikasiKBBI.lokasi_kuki
    if args.lokasi_kuki:
        lokasi_kuki = Path(args.lokasi_kuki)
    if args.posel is None and args.sandi is None:
        if args.bersihkan:
            return _bersihkan_kuki(lokasi_kuki)
        args.bantuan = True
    if args.bantuan:
        parser.print_help()
        return 0
    try:
        auth = AutentikasiKBBI(
            args.posel, args.sandi, lokasi_kuki=args.lokasi_kuki
        )
    except Galat as e:
        print(e)
        return 1
    else:
        auth.simpan_kuki()
        print(
            "Autentikasi berhasil dan kuki telah disimpan di "
            f"{auth.lokasi_kuki}.\n"
            "Kuki akan otomatis digunakan pada penggunaan KBBI berikutnya."
        )
        if args.lokasi_kuki:
            print(
                "Gunakan opsi --lokasi-kuki yang sama ketika menggunakan KBBI."
            )
    return 0


def _parse_args_utama(args):
    parser = argparse.ArgumentParser(
        description=("Mengambil sebuah laman dalam KBBI Daring."),
        add_help=False,
    )
    parser.add_argument(
        "laman", help='laman yang ingin diambil, contoh: "cinta"'
    )
    parser.add_argument(
        "-h",
        "-b",
        "--help",
        "--bantuan",
        action="help",
        default=argparse.SUPPRESS,
        help="tampilkan pesan bantuan ini dan keluar",
    )
    parser.add_argument(
        "-c",
        "--tanpa-contoh",
        help="jangan tampilkan contoh (bila ada)",
        action="store_false",
        dest="contoh",
    )
    parser.add_argument(
        "-t",
        "--tanpa-terkait",
        help="jangan tampilkan entri terkait (bila ada)",
        action="store_false",
        dest="terkait",
    )
    parser.add_argument(
        "-n",
        "--nonpengguna",
        help="nonaktifkan fitur khusus pengguna",
        action="store_false",
        dest="pengguna",
    )
    parser.add_argument(
        "-j",
        "--json",
        help=(
            "tampilkan hasil (selalu dengan contoh dan entri terkait bila ada)"
            " dalam bentuk JSON"
        ),
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
        "--lokasi-kuki",
        "-l",
        help="lokasi menuju berkas kuki yang akan digunakan untuk autentikasi",
        metavar="L",
    )
    return parser.parse_args(args)


def _keluaran(laman, args):
    if args.json:
        return json.dumps(
            laman.serialisasi(args.pengguna), indent=args.indentasi
        )
    else:
        return laman.__str__(args.contoh, args.terkait, args.pengguna)


def main(argv=None):
    """Program CLI utama."""
    if argv is None:
        argv = sys.argv[1:]
    args = _parse_args_utama(argv)
    auth = None
    lokasi_kuki = AutentikasiKBBI.lokasi_kuki
    if args.lokasi_kuki:
        lokasi_kuki = Path(args.lokasi_kuki)
    if lokasi_kuki.exists():
        auth = AutentikasiKBBI(lokasi_kuki=lokasi_kuki)
    elif args.lokasi_kuki:
        print(KukiTidakDitemukan(lokasi_kuki, posel_sandi=False))
        return 1
    try:
        laman = KBBI(args.laman, auth)
    except Galat as e:
        print(e)
        return 1
    else:
        print(_keluaran(laman, args))
        return 0


def init():
    if __name__ == "__main__":
        return sys.exit(main())


init()
