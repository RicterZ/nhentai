# coding: utf-8
import os
import shutil
import sys
import signal
import platform
import urllib

import urllib3.exceptions

from nhentai import constant
from nhentai.cmdline import cmd_parser, banner, write_config
from nhentai.parser import doujinshi_parser, search_parser, legacy_search_parser, print_doujinshi, favorites_parser
from nhentai.doujinshi import Doujinshi
from nhentai.downloader import Downloader
from nhentai.logger import logger
from nhentai.constant import BASE_URL
from nhentai.utils import generate_html, generate_doc, generate_main_html, generate_metadata_file, \
    paging, check_cookie, signal_handler, DB, move_to_folder


def main():
    banner()

    if sys.version_info < (3, 0, 0):
        logger.error('nhentai now only support Python 3.x')
        sys.exit(1)

    options = cmd_parser()
    logger.info(f'Using mirror: {BASE_URL}')

    # CONFIG['proxy'] will be changed after cmd_parser()
    if constant.CONFIG['proxy']:
        if isinstance(constant.CONFIG['proxy'], dict):
            constant.CONFIG['proxy'] = constant.CONFIG['proxy'].get('http', '')
            logger.warning(f'Update proxy config to: {constant.CONFIG["proxy"]}')
            write_config()

        logger.info(f'Using proxy: {constant.CONFIG["proxy"]}')

    if not constant.CONFIG['template']:
        constant.CONFIG['template'] = 'default'

    logger.info(f'Using viewer template "{constant.CONFIG["template"]}"')

    # check your cookie
    check_cookie()

    doujinshis = []
    doujinshi_ids = []

    page_list = paging(options.page)

    if options.favorites:
        if not options.is_download:
            logger.warning('You do not specify --download option')

        doujinshis = favorites_parser(page=page_list) if options.page else favorites_parser()

    elif options.keyword:
        if constant.CONFIG['language']:
            logger.info(f'Using default language: {constant.CONFIG["language"]}')
            options.keyword += f' language:{constant.CONFIG["language"]}'

        _search_parser = legacy_search_parser if options.legacy else search_parser
        doujinshis = _search_parser(options.keyword, sorting=options.sorting, page=page_list,
                                    is_page_all=options.page_all)

    elif options.artist:
        doujinshis = legacy_search_parser(options.artist, sorting=options.sorting, page=page_list,
                                          is_page_all=options.page_all, type_='ARTIST')

    elif not doujinshi_ids:
        doujinshi_ids = options.id

    print_doujinshi(doujinshis)
    if options.is_download and doujinshis:
        doujinshi_ids = [i['id'] for i in doujinshis]

    if options.is_save_download_history:
        with DB() as db:
            data = map(int, db.get_all())

        doujinshi_ids = list(set(map(int, doujinshi_ids)) - set(data))

    if not options.is_show:
        downloader = Downloader(path=options.output_dir, threads=options.threads,
                                timeout=options.timeout, delay=options.delay,
                                retry=options.retry, exit_on_fail=options.exit_on_fail,
                                no_filename_padding=options.no_filename_padding)

        for doujinshi_id in doujinshi_ids:
            doujinshi_info = doujinshi_parser(doujinshi_id)
            if doujinshi_info:
                doujinshi = Doujinshi(name_format=options.name_format, **doujinshi_info)
            else:
                continue

            if not options.dryrun:
                doujinshi.downloader = downloader

                if doujinshi.check_if_need_download(options):
                    doujinshi.download()
                else:
                    logger.info(f'Skip download doujinshi because a PDF/CBZ file exists of doujinshi {doujinshi.name}')
                    continue

            if options.generate_metadata:
                generate_metadata_file(options.output_dir, doujinshi)

            if options.is_save_download_history:
                with DB() as db:
                    db.add_one(doujinshi.id)

            if not options.is_nohtml:
                generate_html(options.output_dir, doujinshi, template=constant.CONFIG['template'])

            if options.is_cbz:
                generate_doc('cbz', options.output_dir, doujinshi, options.regenerate)

            if options.is_pdf:
                generate_doc('pdf', options.output_dir, doujinshi, options.regenerate)

            if options.move_to_folder:
                if options.is_cbz:
                    move_to_folder(options.output_dir, doujinshi, 'cbz')
                if options.is_pdf:
                    move_to_folder(options.output_dir, doujinshi, 'pdf')

            if options.rm_origin_dir:
                if options.move_to_folder:
                    logger.critical('You specified both --move-to-folder and --rm-origin-dir options, '
                                    'you will not get anything :(')
                shutil.rmtree(os.path.join(options.output_dir, doujinshi.filename), ignore_errors=True)

        if options.main_viewer:
            generate_main_html(options.output_dir)

        if not platform.system() == 'Windows':
            logger.log(16, '🍻 All done.')
        else:
            logger.log(16, 'All done.')

    else:
        for doujinshi_id in doujinshi_ids:
            doujinshi_info = doujinshi_parser(doujinshi_id)
            if doujinshi_info:
                doujinshi = Doujinshi(name_format=options.name_format, **doujinshi_info)
            else:
                continue
            doujinshi.show()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()
