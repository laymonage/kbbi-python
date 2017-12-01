# [WIP] kbbi-python

Modul Python untuk mengambil entri sebuah kata/frase dalam KBBI Daring
(https://kbbi.kemdikbud.go.id).

## Penggunaan

- Clone repositori ini atau unduh kbbi.py
- Letakkan kbbi.py dalam direktori yang Anda inginkan

```python
>>> from kbbi import KBBI
>>> kata = KBBI('kata')
>>> kata.arti
>>> kata.arti_contoh
>>> print(kata)
```
