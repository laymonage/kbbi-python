# Berkontribusi

Apabila Anda ingin berkontribusi, silakan ikuti langkah-langkah berikut.

1. [*Fork*][fork] repositori ini.
2. Klonakan repositori yang sudah Anda *fork* dan masuk ke dalam direktori
   repositori yang baru saja terbuat.

   ```bash
   $ git clone https://github.com/<username>/kbbi-python.git
   $ cd kbbi-python
   ```

   (Silakan gunakan SSH jika Anda ingin).
3. Buat cabang baru untuk pembaruan Anda:

   ```bash
   $ git checkout -b pembaruan-saya
   ```

   (Silakan gunakan `git switch -c pembaruan-saya` untuk `git >= 2.23`).
4. Buat *virtual environment* untuk pengembangan:

   ```bash
   $ python3 -m venv venv
   ```

5. Aktifkan *virtual environment* tersebut:

    ```bash
    $ source venv/bin/activate
    ```

    (Apabila Anda menggunakan Windows, ganti perintah di atas dengan
    ```venv\Scripts\activate.bat```).

6. Instal paket-paket prasyarat untuk pengembangan:

    ```bash
    $ pip install -r requirements-dev.txt
    ```

7. Apabila Anda belum menginstal [`pre-commit`][pre-commit], sangat
   disarankan (tidak wajib) untuk menginstalnya terlebih dahulu
   (`pip install pre-commit`). Apabila Anda sudah, silakan instal *hooks* yang
   digunakan di repositori ini:

   ```bash
   $ pre-commit install
   ```

8. Lakukan pengembangan. Apabila Anda ingin mencoba hasil pengembangan Anda,
   instal `kbbi` dari kode sumber terlebih dahulu:

   ```bash
   $ pip install -e .
   ```

   (Perintah tersebut cukup dijalankan sekali, `kbbi` yang diimpor atau
   dijalankan dengan CLI pada *virtual environment* ini akan otomatis
   sesuai dengan pengembangan yang Anda lakukan).

9. Jika sudah selesai, silakan simpan perubahan Anda:

   ```bash
   $ git add .
   $ git commit -m "Memperbaiki fitur yang ada"
   ```

10. Apabila Anda sudah menginstal *hooks* `pre-commit`, maka proses *linting*
    akan otomatis dijalankan untuk memastikan kode Anda sesuai dengan gaya
    penulisan kode yang diharapkan. Jika Anda tidak menginstalnya, silakan
    periksa manual:

    ```bash
    $ black . -l 79
    $ flake8 --exclude="venv/**"
    $ isort -rc . -sg "venv/**"
    ```

11. Jika terdapat kesalahan gaya penulisan kode, silakan perbaiki terlebih
    dahulu (`black` dan `isort` sudah otomatis memperbaiki, tetapi `flake8`
    tidak).
12. Jika gaya penulisan kode sudah baik, jalankan tes untuk memastikan kode
    Anda lulus tes. Sebelum menjalankan tes, jalankan *server* untuk tes
    terlebih dahulu:

    ```bash
    $ cd tests
    $ ./server.py
    ```

    Selagi *server* aktif, jalankan tes:

    ```bash
    $ pytest
    ```

13. Jika kode Anda belum lulus tes, silakan perbaiki terlebih dahulu dan
    lakukan `git add` dan `git commit` seperlunya.
14. Jika Anda ingin menambahkan kasus uji (misal `"civitas academica"`) untuk
    mendukung perbaikan Anda, gunakan skrip `buat_kasus.py`:

    ```bash
    $ ./buat_kasus.py "civitas academica"
    ```

    Kemudian, tambahkan kasus tersebut ke dalam `list` `laman` yang terdapat
    di dalam `buat_kasus.py` dan sertakan deskripsi singkat mengenai kasus
    tersebut. Jika sudah selesai, `git add` dan `git commit` semua berkas yang
    dihasilkan beserta `buat_kasus.py` yang sudah diperbarui.

15. Unggah pembaruan Anda:

    ```bash
    $ git push origin pembaruan-saya
    ```

16. [Buat Pull Request][pr] baru dari cabang Anda ke cabang `master` repositori
    ini.

[fork]: https://github.com/laymonage/kbbi-python/fork
[pre-commit]: https://pre-commit.com
[pr]: https://github.com/laymonage/kbbi-python/compare
