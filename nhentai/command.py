#!/usr/bin/env python2.7
# coding: utf-8
from __future__ import unicode_literals, print_function
import json
import os
import signal
import platform
import time

from nhentai import constant
from nhentai.cmdline import cmd_parser, banner
from nhentai.parser import doujinshi_parser, search_parser, print_doujinshi, favorites_parser
from nhentai.doujinshi import Doujinshi
from nhentai.downloader import Downloader
from nhentai.logger import logger
from nhentai.constant import NHENTAI_CONFIG_FILE, BASE_URL
from nhentai.utils import generate_html, generate_cbz, generate_main_html, generate_pdf, \
    paging, check_cookie, signal_handler, DB


def main():
    banner()
    options = cmd_parser()
    logger.info('Using mirror: {0}'.format(BASE_URL))

    # CONFIG['proxy'] will be changed after cmd_parser()
    if constant.CONFIG['proxy']:
        logger.info('Using proxy: {0}'.format(constant.CONFIG['proxy']))

    # check your cookie
    check_cookie()

    doujinshis = []
    doujinshi_ids = []
    doujinshi_list = []

    page_list = paging(options.page)

    if options.favorites:
        if not options.is_download:
            logger.warning('You do not specify --download option')

        doujinshis = favorites_parser(page=page_list)

    elif options.keyword:
        if constant.CONFIG['language']:
            logger.info('Using default language: {0}'.format(constant.CONFIG['language']))
            options.keyword += ' language:{}'.format(constant.CONFIG['language'])
        doujinshis = search_parser(options.keyword, sorting=options.sorting, page=page_list,
                                   is_page_all=options.page_all)

    elif not doujinshi_ids:
        doujinshi_ids = options.id

    print_doujinshi(doujinshis)
    if options.is_download and doujinshis:
        doujinshi_ids = [i['id'] for i in doujinshis]

        if options.is_save_download_history:
            with DB() as db:
                data = set(db.get_all())

            doujinshi_ids = list(set(doujinshi_ids) - data)

    if doujinshi_ids:
        for i, id_ in enumerate(doujinshi_ids):
            if options.delay:
                time.sleep(options.delay)

            doujinshi_info = doujinshi_parser(id_)

            if doujinshi_info:
                doujinshi_list.append(Doujinshi(name_format=options.name_format, **doujinshi_info))

            if (i + 1) % 10 == 0:
                logger.info('Progress: %d / %d' % (i + 1, len(doujinshi_ids)))

    if not options.is_show:
        downloader = Downloader(path=options.output_dir, size=options.threads,
                                timeout=options.timeout, delay=options.delay)

        for doujinshi in doujinshi_list:

            doujinshi.downloader = downloader
            doujinshi.download()
            if options.is_save_download_history:
                with DB() as db:
                    db.add_one(doujinshi.id)

            if not options.is_nohtml and not options.is_cbz and not options.is_pdf:
                generate_html(options.output_dir, doujinshi)
            elif options.is_cbz:
                generate_cbz(options.output_dir, doujinshi, options.rm_origin_dir)
            elif options.is_pdf:
                generate_pdf(options.output_dir, doujinshi, options.rm_origin_dir)

        if options.main_viewer:
            generate_main_html(options.output_dir)

        if not platform.system() == 'Windows':
            logger.log(15, '🍻 All done.')
        else:
            logger.log(15, 'All done.')

    else:
        [doujinshi.show() for doujinshi in doujinshi_list]


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
