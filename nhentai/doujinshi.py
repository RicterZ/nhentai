# coding: utf-8

from tabulate import tabulate

from nhentai.constant import DETAIL_URL, IMAGE_URL
from nhentai.logger import logger
from nhentai.utils import format_filename

MAX_FIELD_LENGTH = 100
EXT_MAP = {
    'j': 'jpg',
    'p': 'png',
    'g': 'gif',
}


class DoujinshiInfo(dict):
    def __init__(self, **kwargs):
        super(DoujinshiInfo, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return ''


def trunk_string(string):
    if len(string) >= MAX_FIELD_LENGTH:
        string = string[:MAX_FIELD_LENGTH] + u'…'

    return string


class Doujinshi(object):
    def __init__(self, name=None, pretty_name=None, id=None, img_id=None,
                 ext='', pages=0, name_format='[%i][%a][%t]', **kwargs):
        self.name = name
        self.pretty_name = pretty_name
        self.id = id
        self.img_id = img_id
        self.ext = ext
        self.pages = pages
        self.downloader = None
        self.url = '%s/%d' % (DETAIL_URL, self.id)
        self.info = DoujinshiInfo(**kwargs)

        name_format = name_format.replace('%i', str(self.id))
        name_format = name_format.replace('%a', self.info.artists)

        name_format = name_format.replace('%t', trunk_string(self.name))
        name_format = name_format.replace('%p', trunk_string(self.pretty_name))
        name_format = name_format.replace('%s', trunk_string(self.info.subtitle))
        self.filename = format_filename(name_format)

        self.table = [
            ["Parodies", self.info.parodies],
            ["Doujinshi", self.name],
            ["Subtitle", self.info.subtitle],
            ["Characters", self.info.characters],
            ["Authors", self.info.artists],
            ["Languages", self.info.languages],
            ["Tags", self.info.tags],
            ["URL", self.url],
            ["Pages", self.pages],
        ]

    def __repr__(self):
        return '<Doujinshi: {0}>'.format(self.name)

    def show(self):

        logger.info(u'Print doujinshi information of {0}\n{1}'.format(self.id, tabulate(self.table)))

    def download(self, regenerate_cbz=False):
        logger.info('Starting to download doujinshi: %s' % self.name)
        if self.downloader:
            download_queue = []
            if len(self.ext) != self.pages:
                logger.warning('Page count and ext count do not equal')

            for i in range(1, min(self.pages, len(self.ext)) + 1):
                download_queue.append('%s/%d/%d.%s' % (IMAGE_URL, int(self.img_id), i, self.ext[i - 1]))

            self.downloader.download(download_queue, self.filename, regenerate_cbz=regenerate_cbz)
        else:
            logger.critical('Downloader has not been loaded')


if __name__ == '__main__':
    test = Doujinshi(name='test nhentai doujinshi', id=1)
    print(test)
    test.show()
    try:
        test.download()
    except Exception as e:
        print('Exception: %s' % str(e))
