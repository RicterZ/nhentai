# coding: utf-8
from __future__ import print_function
import os
import sys
from optparse import OptionParser
try:
    from itertools import ifilter as filter
except ImportError:
    pass

import nhentai.constant as constant
from nhentai import __version__
from nhentai.utils import urlparse, generate_html
from nhentai.logger import logger

try:
    if sys.version_info < (3, 0, 0):
        import codecs
        import locale
        sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        sys.stderr = codecs.getwriter(locale.getpreferredencoding())(sys.stderr)

except NameError:
    # python3
    pass


def banner():
    logger.info(u'''nHentai ver %s: あなたも変態。 いいね?
       _   _            _        _
 _ __ | | | | ___ _ __ | |_ __ _(_)
| '_ \| |_| |/ _ \ '_ \| __/ _` | |
| | | |  _  |  __/ | | | || (_| | |
|_| |_|_| |_|\___|_| |_|\__\__,_|_|
''' % __version__)


def cmd_parser():
    parser = OptionParser('\n  nhentai --search [keyword] --download'
                          '\n  NHENTAI=http://h.loli.club nhentai --id [ID ...]'
                          '\n  nhentai --file [filename]'    
                          '\n\nEnvironment Variable:\n'
                          '  NHENTAI                 nhentai mirror url')
    # operation options
    parser.add_option('--download', '-D', dest='is_download', action='store_true',
                      help='download doujinshi (for search results)')
    parser.add_option('--show', '-S', dest='is_show', action='store_true', help='just show the doujinshi information')

    # doujinshi options
    parser.add_option('--id', type='string', dest='id', action='store', help='doujinshi ids set, e.g. 1,2,3')
    parser.add_option('--search', '-s', type='string', dest='keyword', action='store', help='search doujinshi by keyword')
    parser.add_option('--tag', type='string', dest='tag', action='store', help='download doujinshi by tag')
    parser.add_option('--favorites', '-F', action='store_true', dest='favorites',
                      help='list or download your favorites.')

    # page options
    parser.add_option('--page', type='int', dest='page', action='store', default=1,
                      help='page number of search results')
    parser.add_option('--max-page', type='int', dest='max_page', action='store', default=1,
                      help='The max page when recursive download tagged doujinshi')

    # download options
    parser.add_option('--output', '-o', type='string', dest='output_dir', action='store', default='',
                      help='output dir')
    parser.add_option('--threads', '-t', type='int', dest='threads', action='store', default=5,
                      help='thread count for downloading doujinshi')
    parser.add_option('--timeout', '-T', type='int', dest='timeout', action='store', default=30,
                      help='timeout for downloading doujinshi')
    parser.add_option('--delay', '-d', type='int', dest='delay', action='store', default=0,
                      help='slow down between downloading every doujinshi')
    parser.add_option('--proxy', '-p', type='string', dest='proxy', action='store', default='',
                      help='uses a proxy, for example: http://127.0.0.1:1080')
    parser.add_option('--file',  '-f', type='string', dest='file', action='store', help='read gallery IDs from file.')
    parser.add_option('--format', type='string', dest='name_format', action='store',
                      help='format the saved folder name', default='[%i][%a][%t]')

    # generate options
    parser.add_option('--html', dest='html_viewer', action='store_true',
                      help='generate a html viewer at current directory')
    parser.add_option('--no-html', dest='is_nohtml', action='store_true',
                      help='don\'t generate HTML after downloading')
    parser.add_option('--cbz', '-C', dest='is_cbz', action='store_true',
                      help='generate Comic Book CBZ File')
    parser.add_option('--rm-origin-dir', dest='rm_origin_dir', action='store_true', default=False,
                      help='remove downloaded doujinshi dir when generated CBZ file.')

    # nhentai options
    parser.add_option('--cookie', type='str', dest='cookie', action='store',
                      help='set cookie of nhentai to bypass Google recaptcha')

    try:
        sys.argv = list(map(lambda x: unicode(x.decode(sys.stdin.encoding)), sys.argv))
    except (NameError, TypeError):
        pass
    except UnicodeDecodeError:
        exit(0)

    args, _ = parser.parse_args(sys.argv[1:])

    if args.html_viewer:
        generate_html()
        exit(0)

    if os.path.exists(os.path.join(constant.NHENTAI_HOME, 'cookie')):
        with open(os.path.join(constant.NHENTAI_HOME, 'cookie'), 'r') as f:
            constant.COOKIE = f.read()

    if args.cookie:
        try:
            if not os.path.exists(constant.NHENTAI_HOME):
                os.mkdir(constant.NHENTAI_HOME)

            with open(os.path.join(constant.NHENTAI_HOME, 'cookie'), 'w') as f:
                f.write(args.cookie)
        except Exception as e:
            logger.error('Cannot create NHENTAI_HOME: {}'.format(str(e)))
            exit(1)

        logger.info('Cookie saved.')
        exit(0)

    '''
    if args.login:
        try:
            _, _ = args.login.split(':', 1)
        except ValueError:
            logger.error('Invalid `username:password` pair.')
            exit(1)

        if not args.is_download:
            logger.warning('YOU DO NOT SPECIFY `--download` OPTION !!!')
    '''

    if args.favorites:
        if not constant.COOKIE:
            logger.warning('Cookie has not been set, please use `nhentai --cookie \'COOKIE\'` to set it.')
            exit(1)

    if args.id:
        _ = map(lambda id_: id_.strip(), args.id.split(','))
        args.id = set(map(int, filter(lambda id_: id_.isdigit(), _)))

    if args.file:
        with open(args.file, 'r') as f:
            _ = map(lambda id: id.strip(), f.readlines())
            args.id = set(map(int, filter(lambda id_: id_.isdigit(), _)))

    if (args.is_download or args.is_show) and not args.id and not args.keyword and \
            not args.tag and not args.favorites:
        logger.critical('Doujinshi id(s) are required for downloading')
        parser.print_help()
        exit(1)

    if not args.keyword and not args.id and not args.tag and not args.favorites:
        parser.print_help()
        exit(1)

    if args.threads <= 0:
        args.threads = 1

    elif args.threads > 15:
        logger.critical('Maximum number of used threads is 15')
        exit(1)

    if args.proxy:
        proxy_url = urlparse(args.proxy)
        if proxy_url.scheme not in ('http', 'https'):
            logger.error('Invalid protocol \'{0}\' of proxy, ignored'.format(proxy_url.scheme))
        else:
            constant.PROXY = {'http': args.proxy, 'https': args.proxy}

    return args
