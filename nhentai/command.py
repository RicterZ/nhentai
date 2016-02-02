#!/usr/bin/env python2.7
#coding: utf-8
import signal
from cmdline import cmd_parser, banner
from parser import dojinshi_parser, search_parser, print_dojinshi
from dojinshi import Dojinshi
from downloader import Downloader
from logger import logger


def main():
    banner()
    options = cmd_parser()

    logger.log(15, 'nHentai: あなたも変態。 いいね?')

    dojinshi_ids = []
    dojinshi_list = []

    if options.keyword:
        dojinshis = search_parser(options.keyword, options.page)
        print_dojinshi(dojinshis)
        if options.is_download:
            dojinshi_ids = map(lambda d: d['id'], dojinshis)
    else:
        dojinshi_ids = options.ids

    if dojinshi_ids:
        for id in dojinshi_ids:
            dojinshi_info = dojinshi_parser(id)
            dojinshi_list.append(Dojinshi(**dojinshi_info))
    else:
        raise SystemExit

    if options.is_download:
        downloader = Downloader(path=options.saved_path,
                                thread=options.threads, timeout=options.timeout)
        for dojinshi in dojinshi_list:
            dojinshi.downloader = downloader
            dojinshi.download()
    else:
        map(lambda dojinshi: dojinshi.show(), dojinshi_list)

    logger.log(15, u'🍺 All done.')


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Quit.')
    raise SystemExit

signal.signal(signal.SIGINT, signal_handler)
if __name__ == '__main__':
    main()