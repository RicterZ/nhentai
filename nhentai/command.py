#!/usr/bin/env python2.7
# coding: utf-8
import signal
from cmdline import cmd_parser, banner
from parser import doujinshi_parser, search_parser, print_doujinshi
from doujinshi import Doujinshi
from downloader import Downloader
from logger import logger


def main():
    banner()
    options = cmd_parser()

    logger.log(15, 'nHentai: あなたも変態。 いいね?')

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
        raise SystemExit

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
    raise SystemExit


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
