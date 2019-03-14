'''
kbbi-python
https://kbbi.kemdikbud.go.id

Mengambil laman sebuah kata/frasa dalam KBBI Daring.

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
        dasar = judul.find(class_='rootword')
        nomor = judul.find('sup', recursive=False)
        lafal = judul.find(class_='syllable')
        bentuk_tidak_baku = judul.find('small')
        makna = entri.find_all('li')

        self.nama = ambil_teks_dalam_label(judul)
        self.nomor = nomor.text.strip() if nomor else ''
        self.kata_dasar = ''
        self._init_kata_dasar(dasar)
        self.pelafalan = lafal.text.strip() if lafal else ''

        self.bentuk_tidak_baku = []
        if bentuk_tidak_baku:
            bentuk_tidak_baku = bentuk_tidak_baku.find_all('b')
            self.bentuk_tidak_baku = ''.join(
                e.text.strip() for e in bentuk_tidak_baku
            ).split(', ')

        self.makna = [Makna(m) for m in makna]

    def _init_kata_dasar(self, dasar):
        if dasar:
            dasar = dasar.find('a')
            dasar_no = dasar.find('sup')
            self.kata_dasar = ambil_teks_dalam_label(dasar)
            if dasar_no: self.kata_dasar += ' [{}]'.format(dasar_no.text.strip())

    def serialisasi(self):
        return {
            "nama": self.nama,
            "nomor": self.nomor,
            "kata_dasar": self.kata_dasar,
            "pelafalan": self.pelafalan,
            "bentuk_tidak_baku": self.bentuk_tidak_baku,
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
        hasil += " [{}]".format(self.nomor) if self.nomor else ''
        hasil = self.kata_dasar + " » " + hasil if self.kata_dasar else hasil
        return hasil

    def _bentuk_tidak_baku(self):
        return (
            'Bentuk tidak baku: ' + ', '.join(self.bentuk_tidak_baku)
            if self.bentuk_tidak_baku else ''
        )

    def __str__(self):
        hasil = self._nama()
        if self.pelafalan: hasil += '  ' + self.pelafalan
        if self.bentuk_tidak_baku: hasil += '\n' + self._bentuk_tidak_baku()
        return hasil + '\n' + self._makna()

    def __repr__(self):
        return "<Entri: {}>".format(self._nama())


class Makna:
    def __init__(self, makna_label):
        baku = makna_label.find('a')
        kelas = makna_label.find(color='red').find_all('span')
        submakna = ambil_teks_dalam_label(makna_label).rstrip(':')

        if baku: submakna += ' ' + baku.text.strip()

        self.kelas = {k.text.strip(): k['title'] for k in kelas}
        self.submakna = submakna.split('; ')
        self._init_contoh(makna_label)

    def _init_contoh(self, makna_label):
        indeks = makna_label.text.find(': ')
        if indeks != -1:
            contoh = makna_label.text[indeks + 2:].strip()
            self.contoh = contoh.split('; ')
        else:
            self.contoh = ''

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
