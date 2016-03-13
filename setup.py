#!/usr/bin/env python3
from setuptools import find_packages,setup

VERSION = '0.1.0.dev1'

install_requires = [
    'beautifulsoup4>=4.4.1',
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
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=install_requires,
    license="MIT",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5', 
    ],
)
