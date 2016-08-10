#!/usr/bin/env python2.7
# coding: utf-8
import signal

from nhentai.cmdline import cmd_parser, banner
from nhentai.parser import doujinshi_parser, search_parser, print_doujinshi
from nhentai.doujinshi import Doujinshi
from nhentai.downloader import Downloader
from nhentai.logger import logger


def main():
    banner()
    options = cmd_parser()

    doujinshi_ids = []
    doujinshi_list = []

    if options.keyword:
        doujinshis = search_parser(options.keyword, options.page)
        print_doujinshi(doujinshis)
        if options.is_download:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)
    else:
        doujinshi_ids = options.ids

    if doujinshi_ids:
        for id in doujinshi_ids:
            doujinshi_info = doujinshi_parser(id)
            doujinshi_list.append(Doujinshi(**doujinshi_info))
    else:
        exit(0)

    if options.is_download:
        downloader = Downloader(path=options.saved_path,
                                thread=options.threads, timeout=options.timeout)
        for doujinshi in doujinshi_list:
            doujinshi.downloader = downloader
            doujinshi.download()
    else:
        map(lambda doujinshi: doujinshi.show(), doujinshi_list)

    logger.log(15, u'🍺 All done.')


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Quit.')
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
