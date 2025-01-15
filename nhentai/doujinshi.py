# coding: utf-8
import os

from tabulate import tabulate

from nhentai.constant import DETAIL_URL, IMAGE_URL
from nhentai.logger import logger
from nhentai.utils import format_filename


EXT_MAP = {
    'j': 'jpg',
    'p': 'png',
    'g': 'gif',
    'w': 'webp',
}


class DoujinshiInfo(dict):
    def __init__(self, **kwargs):
        super(DoujinshiInfo, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            ret = dict.__getitem__(self, item)
            return ret if ret else 'Unknown'
        except KeyError:
            return 'Unknown'


class Doujinshi(object):
    def __init__(self, name=None, pretty_name=None, id=None, favorite_counts=0, img_id=None,
                 ext='', pages=0, name_format='[%i][%a][%t]', **kwargs):
        self.name = name
        self.pretty_name = pretty_name
        self.id = id
        self.favorite_counts = favorite_counts
        self.img_id = img_id
        self.ext = ext
        self.pages = pages
        self.downloader = None
        self.url = f'{DETAIL_URL}/{self.id}'
        self.info = DoujinshiInfo(**kwargs)

        ag_value = self.info.groups if self.info.artists == 'Unknown' else self.info.artists
        name_format = name_format.replace('%ag', format_filename(ag_value))

        name_format = name_format.replace('%i', format_filename(str(self.id)))
        name_format = name_format.replace('%f', format_filename(str(self.favorite_counts)))
        name_format = name_format.replace('%a', format_filename(self.info.artists))
        name_format = name_format.replace('%g', format_filename(self.info.groups))

        name_format = name_format.replace('%t', format_filename(self.name))
        name_format = name_format.replace('%p', format_filename(self.pretty_name))
        name_format = name_format.replace('%s', format_filename(self.info.subtitle))
        self.filename = format_filename(name_format, 255, True)

        self.table = [
            ['Parodies', self.info.parodies],
            ['Title', self.name],
            ['Subtitle', self.info.subtitle],
            ['Date', self.info.date],
            ['Characters', self.info.characters],
            ['Authors', self.info.artists],
            ['Groups', self.info.groups],
            ['Languages', self.info.languages],
            ['Tags', self.info.tags],
            ['Favorite Counts', self.favorite_counts],
            ['URL', self.url],
            ['Pages', self.pages],
        ]

    def __repr__(self):
        return f'<Doujinshi: {self.name}>'

    def show(self):
        logger.info(f'Print doujinshi information of {self.id}\n{tabulate(self.table)}')

    def check_if_need_download(self, options):
        base_path = os.path.join(self.downloader.path, self.filename)

        # regenerate, re-download
        if options.regenerate:
            return True

        # pdf or cbz file exists, skip re-download
        # doujinshi directory may not exist b/c of --rm-origin-dir option set.
        # user should pass --regenerate option to get back origin dir.
        ret_pdf = ret_cbz = None
        if options.is_pdf:
            ret_pdf = os.path.exists(f'{base_path}.pdf') or os.path.exists(f'{base_path}/{self.filename}.pdf')

        if options.is_cbz:
            ret_cbz = os.path.exists(f'{base_path}.cbz') or os.path.exists(f'{base_path}/{self.filename}.cbz')

        ret = list(filter(lambda s: s is not None, [ret_cbz, ret_pdf]))
        if ret and all(ret):
            return False

        # doujinshi directory doesn't exist, re-download
        if not (os.path.exists(base_path) and os.path.isdir(base_path)):
            return True

        # fallback
        return True

    def download(self):
        logger.info(f'Starting to download doujinshi: {self.name}')
        if self.downloader:
            download_queue = []
            if len(self.ext) != self.pages:
                logger.warning('Page count and ext count do not equal')

            for i in range(1, min(self.pages, len(self.ext)) + 1):
                download_queue.append(f'{IMAGE_URL}/{self.img_id}/{i}.{self.ext[i-1]}')

            return self.downloader.start_download(download_queue, self.filename)
        else:
            logger.critical('Downloader has not been loaded')
            return False


if __name__ == '__main__':
    test = Doujinshi(name='test nhentai doujinshi', id=1)
    print(test)
    test.show()
    try:
        test.download()
    except Exception as e:
        print(f'Exception: {e}')
