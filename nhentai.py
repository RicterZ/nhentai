#!/usr/bin/env python
#coding: utf-8

from hentai.cmdline import cmd_parser, banner
from hentai.parser import dojinshi_parser, search_parser, print_dojinshi
from hentai.dojinshi import Dojinshi
from hentai.downloader import Downloader
from hentai.logger import logger


__version__ = '0.1'


def main():
    banner()
    options = cmd_parser()

    logger.log(15, 'nHentai: あなたも変態。 いいね?')

    dojinshi_ids = []
    dojinshi_list = []

    if options.keyword:
        dojinshis = search_parser(options.keyword, options.page)
        if options.is_download:
            dojinshi_ids = map(lambda d: d['id'], dojinshis)
        else:
            print_dojinshi(dojinshis)
    else:
        dojinshi_ids = options.ids

    if dojinshi_ids:
        for id in dojinshi_ids:
            dojinshi_info = dojinshi_parser(id)
            dojinshi_list.append(Dojinshi(**dojinshi_info))
    else:
        logger.log(15, 'Nothing has been done.')
        raise SystemExit

    if options.is_download:
        downloader = Downloader(path=options.saved_path, thread=options.threads)
        for dojinshi in dojinshi_list:
            dojinshi.downloader = downloader
            dojinshi.download()
    else:
        map(lambda dojinshi: dojinshi.show(), dojinshi_list)

    logger.log(15, u'🍺 All done.')


if __name__ == '__main__':
    main()