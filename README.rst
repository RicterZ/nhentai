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
**IMPORTANT**: To bypass the nhentai frequency limit, you should use `--cookie` option to store your cookie.
*The default download folder will be the path where you run the command (CLI path).*


Set your nhentai cookie against captcha:

.. code-block:: bash

    nhentai --cookie 'YOUR COOKIE FROM nhentai.net'

Download specified doujinshi:

.. code-block:: bash

    nhentai --id=123855,123866

Download doujinshi with ids specified in a file (doujinshi ids split by line):

.. code-block:: bash

    nhentai --file=doujinshi.txt

Search a keyword and download the first page:

.. code-block:: bash

    nhentai --search="tomori" --page=1 --download

Download by tag name:

.. code-block:: bash

    nhentai --tag lolicon --download --page=2

Download your favorites with delay:

.. code-block:: bash

    nhentai --favorites --download --delay 1

Format output doujinshi folder name:

.. code-block:: bash

    nhentai --id 261100 --format '[%i]%s'

Supported doujinshi folder formatter:

- %i: Doujinshi id
- %t: Doujinshi name
- %s: Doujinshi subtitle (translated name)
- %a: Doujinshi authors' name


Other options:

.. code-block::

    Options:
      # Operation options
      -h, --help            show this help message and exit
      -D, --download        download doujinshi (for search results)
      -S, --show            just show the doujinshi information

      # Doujinshi options
      --id=ID               doujinshi ids set, e.g. 1,2,3
      -s KEYWORD, --search=KEYWORD
                            search doujinshi by keyword
      --tag=TAG             download doujinshi by tag
      -F, --favorites       list or download your favorites.

      # Multi-page options
      --page=PAGE           page number of search results
      --max-page=MAX_PAGE   The max page when recursive download tagged doujinshi

      # Download options
      -o OUTPUT_DIR, --output=OUTPUT_DIR
                            output dir
      -t THREADS, --threads=THREADS
                            thread count for downloading doujinshi
      -T TIMEOUT, --timeout=TIMEOUT
                            timeout for downloading doujinshi
      -d DELAY, --delay=DELAY
                            slow down between downloading every doujinshi
      -p PROXY, --proxy=PROXY
                            uses a proxy, for example: http://127.0.0.1:1080
      -f FILE, --file=FILE  read gallery IDs from file.
      --format=NAME_FORMAT  format the saved folder name

      # Generating options
      --html                generate a html viewer at current directory
      --no-html             don't generate HTML after downloading
      -C, --cbz             generate Comic Book CBZ File
      --rm-origin-dir       remove downloaded doujinshi dir when generated CBZ
                            file.

      # nHentai options
      --cookie=COOKIE       set cookie of nhentai to bypass Google recaptcha


==============
nHentai Mirror
==============
If you want to use a mirror, you should set up a reverse proxy of `nhentai.net` and `i.nhentai.net`.
For example:

.. code-block:: 

    i.h.loli.club -> i.nhentai.net
    h.loli.club -> nhentai.net

Set `NHENTAI` env var to your nhentai mirror.

.. code-block:: bash

    NHENTAI=http://h.loli.club nhentai --id 123456


.. image:: ./images/search.png?raw=true
    :alt: nhentai
    :align: center
.. image:: ./images/download.png?raw=true
    :alt: nhentai
    :align: center
.. image:: ./images/viewer.png?raw=true
    :alt: nhentai
    :align: center

============
あなたも変態
============
.. image:: ./images/image.jpg?raw=true
    :alt: nhentai
    :align: center



.. |travis| image:: https://travis-ci.org/RicterZ/nhentai.svg?branch=master
   :target: https://travis-ci.org/RicterZ/nhentai

.. |pypi| image:: https://img.shields.io/pypi/dm/nhentai.svg
   :target: https://pypi.org/project/nhentai/

.. |license| image:: https://img.shields.io/github/license/ricterz/nhentai.svg
   :target: https://github.com/RicterZ/nhentai/blob/master/LICENSE
