'''
File setup untuk modul KBBI.
'''

from setuptools import setup
setup(
    name='kbbi',
    version='0.2.1',
    py_modules=['kbbi'],
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    description=('A Python module that scraps an entry in KBBI'
                 '(https://kbbi.kemdikbud.go.id)'),
    author='sage',
    author_email='laymonage@gmail.com',
    url='https://github.com/laymonage/kbbi-python',
    download_url=('https://github.com/laymonage/kbbi-python/'
                  'archive/0.2.1.tar.gz'),
    keywords=['kbbi', 'kamus', 'indonesia'],
    classifiers=[],
)
