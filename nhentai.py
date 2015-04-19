from hentai.cmdline import cmd_parser
from hentai.parser import dojinshi_parser
from hentai.dojinshi import Dojinshi
from hentai.downloader import Downloader


def main():
    options = cmd_parser()
    dojinshi = None

    if options.id:
        dojinshi_info = dojinshi_parser(options.id)
        dojinshi = Dojinshi(**dojinshi_info)
    elif options.keyword:
        pass
    else:
        raise SystemExit

    dojinshi.show()
    if options.is_download:
        dojinshi.downloader = Downloader()
        dojinshi.download()


if __name__ == '__main__':
    main()