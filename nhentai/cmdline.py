#coding: utf-8
from __future__ import print_function
from optparse import OptionParser
from logger import logger
try:
    from itertools import ifilter as filter
except ImportError:
    pass


def banner():
    print('''       _   _            _        _
 _ __ | | | | ___ _ __ | |_ __ _(_)
| '_ \| |_| |/ _ \ '_ \| __/ _` | |
| | | |  _  |  __/ | | | || (_| | |
|_| |_|_| |_|\___|_| |_|\__\__,_|_|
''')


def cmd_parser():
    parser = OptionParser()
    parser.add_option('--download', dest='is_download', action='store_true', help='download dojinshi or not')
    parser.add_option('--id', type='int', dest='id', action='store', help='dojinshi id of nhentai')
    parser.add_option('--ids', type='str', dest='ids', action='store', help='dojinshi id set, e.g. 1,2,3')
    parser.add_option('--search', type='string', dest='keyword', action='store', help='keyword searched')
    parser.add_option('--page', type='int', dest='page', action='store', default=1,
                      help='page number of search result')
    parser.add_option('--path', type='string', dest='saved_path', action='store', default='',
                      help='path which save the dojinshi')
    parser.add_option('--threads', '-t', type='int', dest='threads', action='store', default=1,
                      help='thread count of download dojinshi')
    parser.add_option('--timeout', type='int', dest='timeout', action='store', default=30,
                      help='timeout of download dojinshi')
    args, _ = parser.parse_args()

    if args.ids:
        _ = map(lambda id: id.strip(), args.ids.split(','))
        args.ids = set(map(int, filter(lambda id: id.isdigit(), _)))

    if args.is_download and not args.id and not args.ids and not args.keyword:
        logger.critical('Dojinshi id/ids is required for downloading')
        parser.print_help()
        raise SystemExit

    if args.id:
        args.ids = (args.id, ) if not args.ids else args.ids

    if not args.keyword and not args.ids:
        parser.print_help()
        raise SystemExit

    if args.threads <= 0:
        args.threads = 1
    elif args.threads > 10:
        logger.critical('Maximum number of used threads is 10')
        raise SystemExit

    return args
