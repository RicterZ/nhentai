from setuptools import setup, find_packages
from nhentai import __version__, __author__, __email__

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

setup(
    name='nhentai',
    version=__version__,
    packages=find_packages(),

    author=__author__,
    author_email=__email__,
    keywords='nhentai, dojinshi',
    description='nhentai.net dojinshis downloader',
    url='https://github.com/RicterZ/nhentai',
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