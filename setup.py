#!/usr/bin/env python3
from setuptools import setup

VERSION = '0.0.1'

install_requires = [
    'requests>=2.4.3',
]

setup(
    name="Library API",
    version=VERSION,
    description="Privides access to various libraries (book borrowing places, not code libraries).",
    author=', '.join((
        'Benjamin Howe <ben@bh96.uk>',
        'Scott Street <scott@spru.sr>',
    )),
    url="https://github.com/BenjaminEHowe/library-api",
    packages=["library_api"],
    install_requires=install_requires,
    license="MIT",
)
