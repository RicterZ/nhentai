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

    logger.log(15, 'nHentai: あなたも変態。 いいね?')

    dojinshi_list = []
    if options.ids:
        for id in options.ids:
            dojinshi_info = dojinshi_parser(id)
            dojinshi_list.append(Dojinshi(**dojinshi_info))
    elif options.keyword:
        pass
    else:
        raise SystemExit

    if options.is_download:
        downloader = Downloader(path=options.saved_path, thread=options.threads)
        for dojinshi in dojinshi_list:
            dojinshi.downloader = downloader
            dojinshi.download()
    else:
        map(lambda dojinshi: dojinshi.show(), dojinshi_list)


if __name__ == '__main__':
    main()