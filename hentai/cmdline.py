from optparse import OptionParser


def cmd_parser():
    parser = OptionParser()
    parser.add_option('--search', type='string', dest='keyword', action='store')
    parser.add_option('--download', dest='is_download', action='store_true')
    parser.add_option('--id', type='int', dest='id', action='store')

    args, _ = parser.parse_args()
    return args
