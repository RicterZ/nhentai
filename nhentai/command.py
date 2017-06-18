#!/usr/bin/env python2.7
# coding: utf-8
from __future__ import unicode_literals, print_function
import os
import signal
import platform

from nhentai.cmdline import cmd_parser, banner
from nhentai.parser import doujinshi_parser, search_parser, print_doujinshi
from nhentai.doujinshi import Doujinshi
from nhentai.downloader import Downloader
from nhentai.logger import logger
from nhentai.constant import BASE_URL


def main():
    banner()
    logger.info('Using mirror: {0}'.format(BASE_URL))
    options = cmd_parser()

    doujinshi_ids = []
    doujinshi_list = []

    if options.keyword:
        doujinshis = search_parser(options.keyword, options.page)
        print_doujinshi(doujinshis)
        if options.is_download:
            doujinshi_ids = map(lambda d: d['id'], doujinshis)
    else:
        doujinshi_ids = options.id

    if doujinshi_ids:
        for id in doujinshi_ids:
            doujinshi_info = doujinshi_parser(id)
            doujinshi_list.append(Doujinshi(**doujinshi_info))
    else:
        exit(0)

    if not options.is_show:
        downloader = Downloader(path=options.output_dir,
                                thread=options.threads, timeout=options.timeout)

        for doujinshi in doujinshi_list:
            doujinshi.downloader = downloader
            doujinshi.download()

            image_html = ''
            previous = ''

            doujinshi_dir = os.path.join(options.output_dir, str(doujinshi.id))
            file_list = os.listdir(doujinshi_dir)
            for index, image in enumerate(file_list):
                try:
                    next_ = file_list[file_list.index(image) + 1]
                except IndexError:
                    next_ = ''

                image_html += '<img src="{0}" class="image-item {1}" attr-prev="{2}" attr-next="{3}">\n'\
                    .format(image, 'current' if index == 0 else '', previous, next_)
                previous = image

            with open(os.path.join(os.path.dirname(__file__), 'doujinshi.html'), 'r') as template:
                html = template.read()

            data = html.format(TITLE=doujinshi.name, IMAGES=image_html)
            with open(os.path.join(doujinshi_dir, 'index.html'), 'w') as f:
                f.write(data)

            logger.log(15, 'HTML Viewer has been write to \'{0}\''.format(os.path.join(doujinshi_dir, 'index.html')))

        if not platform.system() == 'Windows':
            logger.log(15, '🍺 All done.')
        else:
            logger.log(15, 'All done.')

    else:
        [doujinshi.show() for doujinshi in doujinshi_list]


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Quit.')
    exit(1)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
