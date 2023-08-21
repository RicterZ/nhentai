nhentai
=======

あなたも変態。 いいね?

|travis|
|pypi|
|version|
|license|


nhentai is a CLI tool for downloading doujinshi from `nhentai.net <https://nhentai.net>`_

GUI version: `https://github.com/edgar1016/nhentai-GUI <https://github.com/edgar1016/nhentai-GUI>`_

===================
Manual Installation
===================
From Github:

.. code-block::

    git clone https://github.com/RicterZ/nhentai
    cd nhentai
    python setup.py install

Build Docker container:

.. code-block::

    git clone https://github.com/RicterZ/nhentai
    cd nhentai
    docker build -t nhentai:latest .
    docker run --rm -it -v ~/Downloads/doujinshi:/output -v ~/.nhentai/:/root/.nhentai nhentai --id 123855

==================
Installation
==================
From PyPI with pip:

.. code-block::

   pip install nhentai

For a self-contained installation, use `pipx <https://github.com/pipxproject/pipx/>`_:

.. code-block::

   pipx install nhentai

Pull from Dockerhub:

.. code-block::

    docker pull ricterz/nhentai
    docker run --rm -it -v ~/Downloads/doujinshi:/output -v ~/.nhentai/:/root/.nhentai ricterz/nhentai --id 123855

On Gentoo Linux:

.. code-block::

    layman -fa glicOne
    sudo emerge net-misc/nhentai

On NixOS:

.. code-block::

    nix-env -iA nixos.nhentai
    
=====
Usage
=====
**⚠️IMPORTANT⚠️**: To bypass the nhentai frequency limit, you should use `--cookie` and `--useragent` options to store your cookie and your user-agent.

.. code-block:: bash

    nhentai --useragent "USER AGENT of YOUR BROWSER"
    nhentai --cookie "YOUR COOKIE FROM nhentai.net"

**NOTE:**

- The format of the cookie is `"csrftoken=TOKEN; sessionid=ID; cf_clearance=CLOUDFLARE"`
- `cf_clearance` cookie and useragent must be set if you encounter "blocked by cloudflare captcha" error. Make sure you use the same IP and useragent as when you got it

| To get csrftoken and sessionid, first login to your nhentai account in web browser, then:
| (Chrome) |ve| |ld| More tools    |ld| Developer tools     |ld| Application |ld| Storage |ld| Cookies |ld| https://nhentai.net
| (Firefox) |hv| |ld| Web Developer |ld| Web Developer Tools                  |ld| Storage |ld| Cookies |ld| https://nhentai.net
| 

.. |hv| unicode:: U+2630 .. https://www.compart.com/en/unicode/U+2630
.. |ve| unicode:: U+22EE .. https://www.compart.com/en/unicode/U+22EE
.. |ld| unicode:: U+2014 .. https://www.compart.com/en/unicode/U+2014

.. image:: https://github.com/RicterZ/nhentai/raw/master/images/usage.png
    :alt: nhentai
    :align: center

*The default download folder will be the path where you run the command (%cd% or $PWD).*

Download specified doujinshi:

.. code-block:: bash

    nhentai --id 123855 123866 123877

Download doujinshi with ids specified in a file (doujinshi ids split by line):

.. code-block:: bash

    nhentai --file=doujinshi.txt

Set search default language

.. code-block:: bash

    nhentai --language=english

Search a keyword and download the first page:

.. code-block:: bash

    nhentai --search="tomori" --page=1 --download
    # you also can download by tags and multiple keywords
    nhentai --search="tag:lolicon, artist:henreader, tag:full color"
    nhentai --search="lolicon, henreader, full color"

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
- %g: Doujinshi groups name
- %p: Doujinshi pretty name
- %ag: Doujinshi authors name or groups name


Other options:

.. code-block::

    Usage:
      nhentai --search [keyword] --download
      NHENTAI=https://nhentai-mirror-url/ nhentai --id [ID ...]
      nhentai --file [filename]

    Environment Variable:
      NHENTAI                 nhentai mirror url

    Options:
      # Operation options, control the program behaviors
      -h, --help            show this help message and exit
      -D, --download        download doujinshi (for search results)
      -S, --show            just show the doujinshi information

      # Doujinshi options, specify id, keyword, etc.
      --id                  doujinshi ids set, e.g. 167680 167681 167682
      -s KEYWORD, --search=KEYWORD
                            search doujinshi by keyword
      -F, --favorites       list or download your favorites

      # Page options, control the page to fetch / download
      --page-all            all search results
      --page=PAGE, --page-range=PAGE
                            page number of search results. e.g. 1,2-5,14
      --sorting=SORTING     sorting of doujinshi (recent / popular /
                            popular-[today|week])

      # Download options, the output directory, threads, timeout, delay, etc.
      -o OUTPUT_DIR, --output=OUTPUT_DIR
                            output dir
      -t THREADS, --threads=THREADS
                            thread count for downloading doujinshi
      -T TIMEOUT, --timeout=TIMEOUT
                            timeout for downloading doujinshi
      -d DELAY, --delay=DELAY
                            slow down between downloading every doujinshi
      --proxy=PROXY         store a proxy, for example: -p "http://127.0.0.1:1080"
      -f FILE, --file=FILE  read gallery IDs from file.
      --format=NAME_FORMAT  format the saved folder name
      --dry-run             Dry run, skip file download

      # Generate options, for generate html viewer, cbz file, pdf file, etc
      --html                generate a html viewer at current directory
      --no-html             don't generate HTML after downloading
      --gen-main            generate a main viewer contain all the doujin in the
                            folder
      -C, --cbz             generate Comic Book CBZ File
      -P, --pdf             generate PDF file
      --rm-origin-dir       remove downloaded doujinshi dir when generated CBZ or
                            PDF file
      --move-to-folder      remove files in doujinshi dir then move new file to folder 
                            when generated CBZ or PDF file  
      --meta                generate a metadata file in doujinshi format
      --regenerate-cbz      regenerate the cbz file if exists

      # nhentai options, set cookie, user-agent, language, remove caches, histories, etc
      --cookie=COOKIE       set cookie of nhentai to bypass Cloudflare captcha
      --useragent=USERAGENT, --user-agent=USERAGENT
                            set useragent to bypass Cloudflare captcha
      --language=LANGUAGE   set default language to parse doujinshis
      --clean-language      set DEFAULT as language to parse doujinshis
      --save-download-history
                            save downloaded doujinshis, whose will be skipped if
                            you re-download them
      --clean-download-history
                            clean download history
      --template=VIEWER_TEMPLATE
                            set viewer template
      --legacy              use legacy searching method

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

    NHENTAI=https://h.loli.club nhentai --id 123456


.. image:: https://github.com/RicterZ/nhentai/raw/master/images/search.png
    :alt: nhentai
    :align: center
.. image:: https://github.com/RicterZ/nhentai/raw/master/images/download.png
    :alt: nhentai
    :align: center
.. image:: https://github.com/RicterZ/nhentai/raw/master/images/viewer.png
    :alt: nhentai
    :align: center


.. |travis| image:: https://travis-ci.org/RicterZ/nhentai.svg?branch=master
   :target: https://travis-ci.org/RicterZ/nhentai

.. |pypi| image:: https://img.shields.io/pypi/dm/nhentai.svg
   :target: https://pypi.org/project/nhentai/

.. |version| image:: https://img.shields.io/pypi/v/nhentai
   :target: https://pypi.org/project/nhentai/

.. |license| image:: https://img.shields.io/github/license/ricterz/nhentai.svg
   :target: https://github.com/RicterZ/nhentai/blob/master/LICENSE
