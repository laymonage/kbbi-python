from kbbi import KBBI, AutentikasiKBBI, GagalAutentikasi


class MockKBBI(KBBI):
    host = "http://localhost:8000"
    _host = KBBI.host

    def __init__(self, kueri, auth=None):
        self._auth = auth
        super().__init__(kueri, auth)
        self.host = self._host
        self.lokasi = self._lokasi

    def _init_lokasi(self):
        super()._init_lokasi()
        auth = "auth" if self._auth is not None else "nonauth"
        self._lokasi = self.lokasi
        self.lokasi = f"{auth}/{self.lokasi}.html".replace("?frasa=", "/")


class MockAutentikasiKBBI(AutentikasiKBBI):
    host = "http://localhost:8000"
    lokasi = "Account/Login.html"

    def _autentikasi(self, posel, sandi):
        try:
            super()._autentikasi(posel, sandi)
        except GagalAutentikasi:
            pass
