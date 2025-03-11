# coding: utf-8

import os
import sys
import json
import nhentai.constant as constant

from urllib.parse import urlparse
from argparse import ArgumentParser

from nhentai import __version__
from nhentai.utils import generate_html, generate_main_html, DB, EXTENSIONS
from nhentai.logger import logger
from nhentai.constant import PATH_SEPARATOR


def banner():
    logger.debug(f'nHentai ver {__version__}: あなたも変態。 いいね?')


def load_config():
    if not os.path.exists(constant.NHENTAI_CONFIG_FILE):
        return

    try:
        with open(constant.NHENTAI_CONFIG_FILE, 'r') as f:
            constant.CONFIG.update(json.load(f))
    except json.JSONDecodeError:
        logger.error('Failed to load config file.')
        write_config()


def write_config():
    if not os.path.exists(constant.NHENTAI_HOME):
        os.mkdir(constant.NHENTAI_HOME)

    with open(constant.NHENTAI_CONFIG_FILE, 'w') as f:
        f.write(json.dumps(constant.CONFIG))


def callback(option, _opt_str, _value, parser):
    if option == '--id':
        pass
    value = []

    for arg in parser.rargs:
        if arg.isdigit():
            value.append(int(arg))
        elif arg.startswith('-'):
            break
        else:
            logger.warning(f'Ignore invalid id {arg}')

    setattr(parser.values, option.dest, value)


def cmd_parser():
    load_config()

    parser = ArgumentParser(
        description='\n  nhentai --search [keyword] --download'
                    '\n  NHENTAI=https://nhentai-mirror-url/ nhentai --id [ID ...]'
                    '\n  nhentai --file [filename]'
                    '\n\nEnvironment Variable:\n'
                    '  NHENTAI                 nhentai mirror url'
    )

    # operation options
    parser.add_argument('--download', '-D', dest='is_download', action='store_true',
                        help='download doujinshi (for search results)')
    parser.add_argument('--no-download', dest='no_download', action='store_true', default=False,
                        help='download doujinshi (for search results)')
    parser.add_argument('--show', '-S', dest='is_show', action='store_true',
                        help='just show the doujinshi information')

    # doujinshi options
    parser.add_argument('--id', dest='id', nargs='+', type=int,
                        help='doujinshi ids set, e.g. 167680 167681 167682')
    parser.add_argument('--search', '-s', type=str, dest='keyword',
                        help='search doujinshi by keyword')
    parser.add_argument('--favorites', '-F', action='store_true', dest='favorites',
                        help='list or download your favorites')
    parser.add_argument('--artist', '-a', type=str, dest='artist',
                        help='list doujinshi by artist name')

    # page options
    parser.add_argument('--page-all', dest='page_all', action='store_true', default=False,
                        help='all search results')
    parser.add_argument('--page', '--page-range', type=str, dest='page',
                        help='page number of search results. e.g. 1,2-5,14')
    parser.add_argument('--sorting', '--sort', dest='sorting', type=str, default='popular',
                        help='sorting of doujinshi (recent / popular / popular-[today|week])',
                        choices=['recent', 'popular', 'popular-today', 'popular-week', 'date'])

    # download options
    parser.add_argument('--output', '-o', type=str, dest='output_dir', default='.',
                        help='output dir')
    parser.add_argument('--threads', '-t', type=int, dest='threads', default=5,
                        help='thread count for downloading doujinshi')
    parser.add_argument('--timeout', '-T', type=int, dest='timeout', default=30,
                        help='timeout for downloading doujinshi')
    parser.add_argument('--delay', '-d', type=int, dest='delay', default=0,
                        help='slow down between downloading every doujinshi')
    parser.add_argument('--retry', type=int, dest='retry', default=3,
                        help='retry times when downloading failed')
    parser.add_argument('--exit-on-fail', dest='exit_on_fail', action='store_true', default=False,
                        help='exit on fail to prevent generating incomplete files')
    parser.add_argument('--proxy', type=str, dest='proxy',
                        help='store a proxy, for example: -p "http://127.0.0.1:1080"')
    parser.add_argument('--file', '-f', type=str, dest='file',
                        help='read gallery IDs from file.')
    parser.add_argument('--format', type=str, dest='name_format', default='[%i][%a][%t]',
                        help='format the saved folder name')

    parser.add_argument('--no-filename-padding', action='store_true', dest='no_filename_padding',
                        default=False, help='no padding in the images filename, such as \'001.jpg\'')

    # generate options
    parser.add_argument('--html', dest='html_viewer', type=str, nargs='?', const='.',
                        help='generate an HTML viewer in the specified directory, or scan all subfolders '
                             'within the entire directory to generate the HTML viewer. By default, current '
                             'working directory is used.')
    parser.add_argument('--no-html', dest='is_nohtml', action='store_true',
                        help='don\'t generate HTML after downloading')
    parser.add_argument('--gen-main', dest='main_viewer', action='store_true',
                        help='generate a main viewer contain all the doujin in the folder')
    parser.add_argument('--cbz', '-C', dest='is_cbz', action='store_true',
                        help='generate Comic Book CBZ File')
    parser.add_argument('--pdf', '-P', dest='is_pdf', action='store_true',
                        help='generate PDF file')

    parser.add_argument('--meta', dest='generate_metadata', action='store_true', default=False,
                        help='generate a metadata file in doujinshi format')
    parser.add_argument('--update-meta', dest='update_metadata', action='store_true', default=False,
                        help='update the metadata file of a doujinshi, update CBZ metadata if exists')

    parser.add_argument('--rm-origin-dir', dest='rm_origin_dir', action='store_true', default=False,
                        help='remove downloaded doujinshi dir when generated CBZ or PDF file')
    parser.add_argument('--move-to-folder', dest='move_to_folder', action='store_true', default=False,
                        help='remove files in doujinshi dir then move new file to folder when generated CBZ or PDF file')

    parser.add_argument('--regenerate', dest='regenerate', action='store_true', default=False,
                        help='regenerate the cbz or pdf file if exists')
    parser.add_argument('--zip', action='store_true', help='Package into a single zip file')

    # nhentai options
    parser.add_argument('--cookie', type=str, dest='cookie',
                        help='set cookie of nhentai to bypass Cloudflare captcha')
    parser.add_argument('--useragent', '--user-agent', type=str, dest='useragent',
                        help='set useragent to bypass Cloudflare captcha')
    parser.add_argument('--language', type=str, dest='language',
                        help='set default language to parse doujinshis')
    parser.add_argument('--clean-language', dest='clean_language', action='store_true', default=False,
                        help='set DEFAULT as language to parse doujinshis')
    parser.add_argument('--save-download-history', dest='is_save_download_history', action='store_true',
                        default=False, help='save downloaded doujinshis, whose will be skipped if you re-download them')
    parser.add_argument('--clean-download-history', action='store_true', default=False, dest='clean_download_history',
                        help='clean download history')
    parser.add_argument('--template', dest='viewer_template', type=str, default='',
                        help='set viewer template')
    parser.add_argument('--legacy', dest='legacy', action='store_true', default=False,
                        help='use legacy searching method')

    args = parser.parse_args()

    if args.html_viewer:
        if not os.path.exists(args.html_viewer):
            logger.error(f'Path \'{args.html_viewer}\' not exists')
            sys.exit(1)

        for root, dirs, files in os.walk(args.html_viewer):
            if not dirs:
                generate_html(output_dir=args.html_viewer, template=constant.CONFIG['template'])
                sys.exit(0)

            for dir_name in dirs:
                # it will scan the entire subdirectories
                doujinshi_dir = os.path.join(root, dir_name)
                items = set(map(lambda s: os.path.splitext(s)[1], os.listdir(doujinshi_dir)))

                # skip directory without any images
                if items & set(EXTENSIONS):
                    generate_html(output_dir=doujinshi_dir, template=constant.CONFIG['template'])

            sys.exit(0)

        sys.exit(0)

    if args.main_viewer and not args.id and not args.keyword and not args.favorites:
        generate_main_html()
        sys.exit(0)

    if args.clean_download_history:
        with DB() as db:
            db.clean_all()

        logger.info('Download history cleaned.')
        sys.exit(0)

    # --- set config ---
    if args.cookie is not None:
        constant.CONFIG['cookie'] = args.cookie.strip()
        write_config()
        logger.info('Cookie saved.')

    if args.useragent is not None:
        constant.CONFIG['useragent'] = args.useragent.strip()
        write_config()
        logger.info('User-Agent saved.')

    if args.language is not None:
        constant.CONFIG['language'] = args.language
        write_config()
        logger.info(f'Default language now set to "{args.language}"')
        # TODO: search without language

    if any([args.cookie, args.useragent, args.language]):
        sys.exit(0)

    if args.proxy is not None:
        proxy_url = urlparse(args.proxy)
        if not args.proxy == '' and proxy_url.scheme not in ('http', 'https', 'socks5', 'socks5h',
                                                             'socks4', 'socks4a'):
            logger.error(f'Invalid protocol "{proxy_url.scheme}" of proxy, ignored')
            sys.exit(0)
        else:
            constant.CONFIG['proxy'] = args.proxy
            logger.info(f'Proxy now set to "{args.proxy}"')
            write_config()
            sys.exit(0)

    if args.viewer_template is not None:
        if not args.viewer_template:
            args.viewer_template = 'default'

        if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                           f'viewer/{args.viewer_template}/index.html')):
            logger.error(f'Template "{args.viewer_template}" does not exists')
            sys.exit(1)
        else:
            constant.CONFIG['template'] = args.viewer_template
            write_config()

    # --- end set config ---

    if args.favorites:
        if not constant.CONFIG['cookie']:
            logger.warning('Cookie has not been set, please use `nhentai --cookie \'COOKIE\'` to set it.')
            sys.exit(1)

    if args.file:
        with open(args.file, 'r') as f:
            _ = [i.strip() for i in f.readlines()]
            args.id = set(int(i) for i in _ if i.isdigit())

    if (args.is_download or args.is_show) and not args.id and not args.keyword and not args.favorites and not args.artist:
        logger.critical('Doujinshi id(s) are required for downloading')
        parser.print_help()
        sys.exit(1)

    if not args.keyword and not args.id and not args.favorites and not args.artist:
        parser.print_help()
        sys.exit(1)

    if args.threads <= 0:
        args.threads = 1

    elif args.threads > 15:
        logger.critical('Maximum number of used threads is 15')
        sys.exit(1)

    return args
