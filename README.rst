nhentai
=======

.. code-block::

           _   _            _        _
     _ __ | | | | ___ _ __ | |_ __ _(_)
    | '_ \| |_| |/ _ \ '_ \| __/ _` | |
    | | | |  _  |  __/ | | | || (_| | |
    |_| |_|_| |_|\___|_| |_|\__\__,_|_|


あなたも変態。 いいね?  
|travis|
|pypi|
|license|


nHentai is a CLI tool for downloading doujinshi from <http://nhentai.net>

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


Set your nhentai cookie aginest captcha:

.. code-block:: bash

    nhentai --cookie 'YOUR COOKIE FROM nhentai.net'

Download specified doujinshi:

.. code-block:: bash

    nhentai --id=123855,123866

Download doujinshi with ids specified in a file:

.. code-block:: bash

    nhentai --file=doujinshi.txt

Search a keyword and download the first page:

.. code-block:: bash

    nhentai --search="tomori" --page=1 --download

Download by tag name:

.. code-block:: bash

    nhentai --tag lolicon --download

Download your favorites:

.. code-block:: bash

    nhentai --favorites --download

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

===========
あなたも変態
===========
![](./images/image.jpg)


.. |travis| image:: https://travis-ci.org/RicterZ/nhentai.svg?branch=master
   :target: https://travis-ci.org/RicterZ/nhentai

.. |pypi| image:: https://img.shields.io/pypi/dm/nhentai.svg
   :target: https://pypi.org/project/nhentai/

.. |license| image:: https://img.shields.io/github/license/ricterz/nhentai.svg
   :target: https://github.com/RicterZ/nhentai/blob/master/LICENSE
