from kbbi import KBBI, AutentikasiKBBI, GagalAutentikasi, TidakDitemukan


class MockKBBI(KBBI):
    host = "http://localhost:8000"
    _host = KBBI.host

    def __init__(self, kueri, auth=None, lokasi=None):
        self._auth = auth
        self._lokasi = lokasi
        self.lokasi = lokasi
        super().__init__(kueri, auth)

    def _cek_autentikasi(self, laman):
        super()._cek_autentikasi(laman)
        self._kembalikan_host_lokasi()

    def _kembalikan_host_lokasi(self):
        self.host = self._host
        self.lokasi = self._lokasi

    @classmethod
    def _init_aman(cls, kueri, auth=None, lokasi=None):
        try:
            return cls(kueri, auth, lokasi)
        except TidakDitemukan as e:
            e.objek._kembalikan_host_lokasi()
            return e.objek

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
