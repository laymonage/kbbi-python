'''
kbbi-python
https://kbbi.kemdikbud.go.id

Mengambil entri sebuah kata/frase dalam KBBI Daring.

Penggunaan:
kata = KBBI('kata')
'''

from urllib.parse import quote
import requests
from bs4 import BeautifulSoup


class KBBI:
    '''
    Sebuah entri di KBBI.
    '''

    class TidakDitemukan(Exception):
        '''
        Galat yang menunjukkan bahwa entri tidak ditemukan dalam KBBI.
        '''
        def __init__(self):
            Exception.__init__(self, 'Entri tidak ditemukan dalam KBBI!')

    def __init__(self, keyword):
        url = 'https://kbbi.kemdikbud.go.id/entri/{}'.format(quote(keyword))
        raw = requests.get(url).text
        if "Entri tidak ditemukan." in raw:
            raise self.TidakDitemukan
        self.arti = []
        self.arti_contoh = []
        isolasi = raw[raw.find('<h2>'):raw.find('<h4>')]
        soup = BeautifulSoup(isolasi, 'html.parser')
        entri = soup.find_all('ol') + soup.find_all('ul')

        for tiap_entri in entri:
            for tiap_arti in tiap_entri.find_all('li'):
                kelas = tiap_arti.find(color="red").get_text().strip()
                arti_lengkap = tiap_arti.get_text().strip()[len(kelas):]

                if ':' in arti_lengkap:
                    arti_saja = arti_lengkap[:arti_lengkap.find(':')]
                else:
                    arti_saja = arti_lengkap

                if kelas:
                    hasil = '({0}) {1}'
                else:
                    hasil = '{1}'

                self.arti_contoh.append(hasil.format(kelas, arti_lengkap))
                self.arti.append(hasil.format(kelas, arti_saja))

    def __str__(self):
        return '\n'.join(self.arti)

    def __repr__(self):
        return str(self)
