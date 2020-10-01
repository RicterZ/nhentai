# coding: utf-8
from __future__ import print_function, unicode_literals
import sys
import codecs
from setuptools import setup, find_packages
from nhentai import __version__, __author__, __email__


with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]


def long_description():
    with codecs.open('README.rst', 'rb') as readme:
        if not sys.version_info < (3, 0, 0):
            return readme.read().decode('utf-8')


setup(
    name='nhentai',
    version=__version__,
    packages=find_packages(),

    author=__author__,
    author_email=__email__,
    keywords=['nhentai', 'doujinshi', 'downloader'],
    description='nhentai.net doujinshis downloader',
    long_description=long_description(),
    url='https://github.com/RicterZ/nhentai',
    download_url='https://github.com/RicterZ/nhentai/tarball/master',
    include_package_data=True,
    zip_safe=False,

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'nhentai = nhentai.command:main',
        ]
    },
    license='MIT',
)
