nhentai
=======

.. code-block::
           _   _            _        _
     _ __ | | | | ___ _ __ | |_ __ _(_)
    | '_ \| |_| |/ _ \ '_ \| __/ _` | |
    | | | |  _  |  __/ | | | || (_| | |
    |_| |_|_| |_|\___|_| |_|\__\__,_|_|


あなたも変態。 いいね?  
[![Build Status](https://travis-ci.org/RicterZ/nhentai.svg?branch=master)](https://travis-ci.org/RicterZ/nhentai) ![nhentai PyPI Downloads](https://img.shields.io/pypi/dm/nhentai.svg) [![license](https://img.shields.io/cocoapods/l/AFNetworking.svg)](https://github.com/RicterZ/nhentai/blob/master/LICENSE)


nHentai is a CLI tool for downloading doujinshi from [nhentai.net](http://nhentai.net).

============
Installation
============

.. code-block::

    git clone https://github.com/RicterZ/nhentai
    cd nhentai
    python setup.py install
    
=====================
Installation (Gentoo)
=====================

.. code-block::

    layman -fa glicOne
    sudo emerge net-misc/nhentai

=====
Usage
=====
**IMPORTANT**: To bypass the nhentai frequency limit, you should use `--login` option to log into nhentai.net.

*The default download folder will be the path where you run the command (CLI path).*

Download specified doujinshi:

.. code-block:: bash

    nhentai --id=123855,123866

Download doujinshi with ids specified in a file:

.. code-block:: bash

    nhentai --file=doujinshi.txt

Search a keyword and download the first page:

.. code-block:: bash

    nhentai --search="tomori" --page=1 --download

Download your favourite doujinshi (login required):

.. code-block:: bash

    nhentai --login "username:password" --download

Download by tag name:

.. code-block:: bash

    nhentai --tag lolicon --download

=======
Options
=======

+ `-t, --thread`: Download threads, max: 10  
+ `--output`:Output dir of saving doujinshi  
+ `--tag`:Download by tag name  
+ `--timeout`: Timeout of downloading each image   
+ `--proxy`: Use proxy, example: http://127.0.0.1:8080/  
+ `--login`: username:password pair of your nhentai account  
+ `--nohtml`: Do not generate HTML  
+ `--cbz`: Generate Comic Book CBZ File  

==============
nHentai Mirror
==============

If you want to use a mirror, you should set up a reverse proxy of `nhentai.net` and `i.nhentai.net`.
For example:

    i.h.loli.club -> i.nhentai.net
    h.loli.club -> nhentai.net

Set `NHENTAI` env var to your nhentai mirror.

.. code-block:: bash

    NHENTAI=http://h.loli.club nhentai --id 123456

![](./images/search.png)  
![](./images/download.png)  
![](./images/viewer.png)  

### あなたも変態
![](./images/image.jpg)
