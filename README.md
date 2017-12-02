# [WIP] kbbi-python

Modul Python untuk mengambil entri sebuah kata/frase dalam KBBI Daring
(https://kbbi.kemdikbud.go.id).


## Instalasi

### Melalui pip

```bash
$ pip install kbbi
```


### Manual

- Clone repositori ini atau unduh kbbi.py
- Letakkan kbbi.py dalam direktori yang Anda inginkan


## Penggunaan

```bash
$ python
```

```python
>>> from kbbi import KBBI
>>> cinta = KBBI('cinta')
>>> print(cinta)
```
```text
(a)  suka sekali; sayang benar
(a)  kasih sekali; terpikat (antara laki-laki dan perempuan)
(a)  ingin sekali; berharap sekali; rindu
(a kl)  susah hati (khawatir); risau
```
```python
>>> for setiap in cinta.arti_contoh:
>>>     print(setiap)
```
```text
(a)  suka sekali; sayang benar: orang tuaku -- kepada kami semua; -- kepada sesama makhluk
(a)  kasih sekali; terpikat (antara laki-laki dan perempuan): sebenarnya dia tidak -- kepada lelaki itu, tetapi hanya menginginkan hartanya
(a)  ingin sekali; berharap sekali; rindu: makin ditindas makin terasa betapa --nya akan kemerdekaan
(a kl)  susah hati (khawatir); risau: tiada terperikan lagi --nya ditinggalkan ayahnya itu
```
