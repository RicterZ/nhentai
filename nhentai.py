#coding: utf-8
from hentai.cmdline import cmd_parser, banner
from hentai.parser import dojinshi_parser
from hentai.dojinshi import Dojinshi
from hentai.downloader import Downloader
from hentai.logger import logger


__version__ = '0.1'


def main():
    banner()
    options = cmd_parser()
    dojinshi = None

    logger.log(15, 'nHentai: あなたも変態。 いいね?')
    if options.id:
        dojinshi_info = dojinshi_parser(options.id)
        dojinshi = Dojinshi(**dojinshi_info)
    elif options.keyword:
        pass
    else:
        raise SystemExit

    if options.is_download:
        dojinshi.downloader = Downloader(path=options.saved_path,
                                         thread=options.threads)
        dojinshi.download()
    else:
        dojinshi.show()


if __name__ == '__main__':
    main()