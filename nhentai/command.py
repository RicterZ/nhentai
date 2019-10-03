#!/usr/bin/env python2.7
# coding: utf-8
from __future__ import unicode_literals, print_function
import signal
import platform
import time

from nhentai.cmdline import cmd_parser, banner
from nhentai.parser import doujinshi_parser, search_parser, print_doujinshi, favorites_parser, tag_parser, login
from nhentai.doujinshi import Doujinshi
from nhentai.downloader import Downloader
from nhentai.logger import logger
from nhentai.constant import BASE_URL
from nhentai.utils import generate_html, generate_cbz, generate_main_html, check_cookie


def main():
    banner()
    options = cmd_parser()
    logger.info('Using mirror: {0}'.format(BASE_URL))

    from nhentai.constant import PROXY
    # constant.PROXY will be changed after cmd_parser()
    if PROXY != {}:
        logger.info('Using proxy: {0}'.format(PROXY))

    # check your cookie
    check_cookie()

    doujinshi_ids = []
    doujinshi_list = []

    if options.favorites:
        if not options.is_download:
            logger.warning('You do not specify --download option')

        doujinshis = favorites_parser()
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.tag:
        doujinshis = tag_parser(options.tag, max_page=options.max_page)
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.artist:
        doujinshis = tag_parser(options.artist, max_page=options.max_page, index=1)
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.character:
        doujinshis = tag_parser(options.character, max_page=options.max_page, index=2)
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.parody:
        doujinshis = tag_parser(options.parody, max_page=options.max_page, index=3)
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.group:
        doujinshis = tag_parser(options.group, max_page=options.max_page, index=4)
        print_doujinshi(doujinshis)
        if options.is_download and doujinshis:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif options.keyword:
        doujinshis = search_parser(options.keyword, options.page)
        print_doujinshi(doujinshis)
        if options.is_download:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)

    elif not doujinshi_ids:
        doujinshi_ids = options.id

    if doujinshi_ids:
        for id_ in doujinshi_ids:
            if options.delay:
                time.sleep(options.delay)
            doujinshi_info = doujinshi_parser(id_)
            doujinshi_list.append(Doujinshi(name_format=options.name_format, **doujinshi_info))

    if not options.is_show:
        downloader = Downloader(path=options.output_dir,
                                thread=options.threads, timeout=options.timeout, delay=options.delay)

        for doujinshi in doujinshi_list:
            doujinshi.downloader = downloader
            doujinshi.download()
            if not options.is_nohtml and not options.is_cbz:
                generate_html(options.output_dir, doujinshi)
            elif options.is_cbz:
                generate_cbz(options.output_dir, doujinshi, options.rm_origin_dir)
        if options.main_viewer:
            generate_main_html(options.output_dir)
        if not platform.system() == 'Windows':
            logger.log(15, '🍻 All done.')
        else:
            logger.log(15, 'All done.')

    else:
        [doujinshi.show() for doujinshi in doujinshi_list]


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Stopping...')
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
