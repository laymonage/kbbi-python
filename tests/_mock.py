from kbbi import KBBI, AutentikasiKBBI, GagalAutentikasi


class MockKBBI(KBBI):
    host = "http://localhost:8000"
    _host = KBBI.host
    lokasi = None

    def __init__(self, kueri, auth=None, lokasi=None):
        self._auth = auth
        self.lokasi = self.lokasi or lokasi
        super().__init__(kueri, auth)
        self.host = self._host
        if lokasi is None:
            self.lokasi = self._lokasi

    def _init_lokasi(self):
        if self.lokasi is not None:
            return
        super()._init_lokasi()
        auth = "auth" if self._auth is not None else "nonauth"
        self._lokasi = self.lokasi
        self.lokasi = f"{auth}/{self.lokasi}.html".replace("?frasa=", "/")


class MockAutentikasiKBBI(AutentikasiKBBI):
    host = "http://localhost:8000"
    lokasi = "Account/Login.html"
    buat_galat = False
    paksa_sukses = False

    def _autentikasi(self, posel, sandi, token, buat_galat=False):
        try:
            super()._autentikasi(posel, sandi, token)
        except GagalAutentikasi as e:
            if self.buat_galat or buat_galat:
                raise e from e
            if not self.paksa_sukses:
                return
        self.sesi.cookies.set(".AspNet.ApplicationCookie", "mockcookie")
