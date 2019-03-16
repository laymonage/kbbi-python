'''
File setup untuk modul KBBI.
'''

from setuptools import find_packages, setup

with open('README.md') as readme:
    long_description = readme.read()

setup(
    name='kbbi',
    version='0.3.0',
    description=(
        "A module that scraps a page in the online Indonesian dictionary (KBBI)"
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/laymonage/kbbi-python',
    author='sage',
    author_email='laymonage@gmail.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Indonesian",
    ],
    keywords=(
        'kbbi kamus bahasa indonesia indonesian natural language scraper'
    ),
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
)
