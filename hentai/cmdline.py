#coding: utf-8
import sys
from optparse import OptionParser
from logger import logger

def banner():
    print '''       _   _            _        _
 _ __ | | | | ___ _ __ | |_ __ _(_)
| '_ \| |_| |/ _ \ '_ \| __/ _` | |
| | | |  _  |  __/ | | | || (_| | |
|_| |_|_| |_|\___|_| |_|\__\__,_|_|
'''


def cmd_parser():
    parser = OptionParser()
    parser.add_option('--search', type='string', dest='keyword', action='store', help='keyword searched')
    parser.add_option('--download', dest='is_download', action='store_true', help='download dojinshi or not')
    parser.add_option('--id', type='int', dest='id', action='store', help='dojinshi id of nhentai')
    parser.add_option('--path', type='string', dest='saved_path', action='store', default='',
                      help='path which save the dojinshi downloaded')
    parser.add_option('--threads', type='int', dest='threads', action='store', default=1,
                      help='thread count of download dojinshi')
    args, _ = parser.parse_args()

    if args.threads <= 0:
        args.threads = 1
    elif args.threads > 10:
        logger.critical('Maximum number of used threads is 10')
        sys.exit()

    if args.is_download and not args.id:
        logger.critical('Dojinshi id is required for downloading')
        sys.exit()

    if args.keyword:
        logger.critical(u'并没有做这个功能_(:3」∠)_')

    return args
