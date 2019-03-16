'''
kbbi-python
https://kbbi.kemdikbud.go.id

Mengambil sebuah laman untuk kata/frasa dalam KBBI Daring.

Penggunaan:
kata = KBBI('kata')
'''

from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


class KBBI:
    '''
    Sebuah laman di KBBI.
    '''

    class TidakDitemukan(Exception):
        '''
        Galat yang menunjukkan bahwa laman tidak ditemukan dalam KBBI.
        '''
        def __init__(self, kata_kunci):
            super().__init__(kata_kunci + ' tidak ditemukan dalam KBBI!')

    def __init__(self, kata_kunci):
        url = 'https://kbbi.kemdikbud.go.id/entri/' + quote(kata_kunci)
        laman = requests.get(url)

        if "Entri tidak ditemukan." in laman.text:
            raise self.TidakDitemukan(kata_kunci)

        self.nama = kata_kunci.lower()
        self.entri = []
        self._init_entri(laman)

    def _init_entri(self, laman):
        sup = BeautifulSoup(laman.text, 'html.parser')
        estr = ''
        for label in sup.find('hr').next_siblings:
            if label.name == 'hr':
                self.entri.append(Entri(estr))
                break
            if label.name == 'h2':
                if estr:
                    self.entri.append(Entri(estr))
                estr = ''
            estr += str(label).strip()

    def serialisasi(self):
        return {
            self.nama: [entri.serialisasi() for entri in self.entri]
        }

    def __str__(self):
        return '\n\n'.join(str(entri) for entri in self.entri)

    def __repr__(self):
        return "<KBBI: {}>".format(self.nama)


class Entri:
    def __init__(self, entri_html):
        entri = BeautifulSoup(entri_html, 'html.parser')
        judul = entri.find('h2')
        dasar = judul.find_all(class_='rootword')
        nomor = judul.find('sup', recursive=False)
        lafal = judul.find(class_='syllable')
        varian = judul.find('small')
        if entri.find(color='darkgreen'):
            makna = [entri]
        else:
            makna = entri.find_all('li')

        self.nama = ambil_teks_dalam_label(judul)
        self.nomor = nomor.text.strip() if nomor else ''
        self.kata_dasar = []
        self._init_kata_dasar(dasar)
        self.pelafalan = lafal.text.strip() if lafal else ''

        self.bentuk_tidak_baku = []
        self.varian = []
        if varian:
            bentuk_tidak_baku = varian.find_all('b')
            if bentuk_tidak_baku:
                self.bentuk_tidak_baku = ''.join(
                    e.text.strip() for e in bentuk_tidak_baku
                ).split(', ')
            else:
                self.varian = varian.text[len('varian: '):].strip().split(', ')

        self.makna = [Makna(m) for m in makna]

    def _init_kata_dasar(self, dasar):
        for d in dasar:
            kata = d.find('a')
            dasar_no = kata.find('sup')
            kata = ambil_teks_dalam_label(kata)
            self.kata_dasar.append(
                kata + ' [{}]'.format(dasar_no.text.strip()) if dasar_no else kata
            )

    def serialisasi(self):
        return {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
            "varian": self.varian,
            "makna": [makna.serialisasi() for makna in self.makna]
        }

    def _makna(self):
        if (len(self.makna) > 1):
            return '\n'.join(
                str(i) + ". " + str(makna)
                for i, makna in enumerate(self.makna, 1)
            )
        return str(self.makna[0])

    def _nama(self):
        hasil = self.nama
        if self.nomor: hasil += " [{}]".format(self.nomor)
        if self.kata_dasar: hasil = " » ".join(self.kata_dasar) + " » " + hasil
        return hasil

    def _varian(self, varian):
        if varian == self.bentuk_tidak_baku:
            nama = "Bentuk tidak baku"
        elif varian == self.varian:
            nama = "Varian"
        else:
            return ''
        return nama + ': ' + ', '.join(varian)

    def __str__(self):
        hasil = self._nama()
        if self.pelafalan: hasil += '  ' + self.pelafalan
        for var in (self.bentuk_tidak_baku, self.varian):
            if var: hasil += '\n' + self._varian(var)
        return hasil + '\n' + self._makna()

    def __repr__(self):
        return "<Entri: {}>".format(self._nama())


class Makna:
    def __init__(self, makna_label):
        self.submakna = ambil_teks_dalam_label(makna_label).rstrip(':')
        baku = makna_label.find('a')
        if baku:
            self.submakna += ' ' + ambil_teks_dalam_label(baku)
            nomor = baku.find('sup')
            if nomor:
                nomor = nomor.text.strip()
                self.submakna += ' [{}]'.format(nomor)
        self._init_kelas(makna_label)
        self.submakna = self.submakna.split('; ')
        self._init_contoh(makna_label)

    def _init_kelas(self, makna_label):
        kelas = makna_label.find(color='red')
        lain = makna_label.find(color='darkgreen')
        if kelas: kelas = kelas.find_all('span')
        if lain:
            self.kelas = {lain.text.strip(): lain['title'].strip()}
            self.submakna = lain.next_sibling.strip()
            self.submakna += ' ' + makna_label.find(color='grey').text.strip()
        else:
            self.kelas = {
                k.text.strip(): k['title'].strip() for k in kelas
            } if kelas else {}

    def _init_contoh(self, makna_label):
        indeks = makna_label.text.find(': ')
        if indeks != -1:
            contoh = makna_label.text[indeks + 2:].strip()
            self.contoh = contoh.split('; ')
        else:
            self.contoh = []

    def serialisasi(self):
        return {
            "kelas": self.kelas,
            "submakna": self.submakna,
            "contoh": self.contoh
        }

    def _kelas(self):
        return ' '.join("({})".format(k) for k in self.kelas)

    def _submakna(self):
        return '; '.join(self.submakna)

    def _contoh(self):
        return '; '.join(self.contoh)

    def __str__(self):
        hasil = self._kelas() + '  ' if self.kelas else ''
        hasil += self._submakna()
        hasil += ': ' + self._contoh() if self.contoh else ''
        return hasil

    def __repr__(self):
        return "<Makna: {}>".format('; '.join(self.submakna))


def ambil_teks_dalam_label(sup):
    return ''.join(i.strip() for i in sup.find_all(text=True, recursive=False))
