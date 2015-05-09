from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [l for l in f.read().splitlines() if l]

setup(
    name='nhentai',
    version='0.1',
    packages=find_packages(),

    author='Ricter',
    author_email='ricterzheng@gmail.com',
    keywords='nhentai, dojinshi',
    description='nhentai.net dojinshis downloader',
    url='https://github.com/RicterZ/nhentai',
    include_package_data=True,

    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'nhentai = nhentai:main',
        ]
    }
)