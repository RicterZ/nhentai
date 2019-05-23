# coding: utf-8
from __future__ import print_function, unicode_literals
from tabulate import tabulate
from future.builtins import range
import string
import os

from nhentai.constant import DETAIL_URL, IMAGE_URL
from nhentai.logger import logger
from nhentai.utils import format_filename


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


class Doujinshi(object):
    def __init__(self, name=None, id=None, img_id=None, ext='', pages=0, name_format='[%i][%a][%t]', path='', **kwargs):
        self.name = name
        self.id = id
        self.img_id = img_id
        self.ext = ext
        self.pages = pages
        self.downloader = None
        self.url = '%s/%d' % (DETAIL_URL, self.id)
        self.path = path
        self.info = DoujinshiInfo(**kwargs)

        name_format = name_format.replace('%i', str(self.id))
        name_format = name_format.replace('%a', self.info.artists)
        name_format = name_format.replace('%t', self.name)
        name_format = name_format.replace('%s', self.info.subtitle)
        self.filename = name_format

        langCode = ""
        for lang in self.info.languages.split(", "):
            if lang != "translated":
                if lang == "chinese": langCode = "zh"
                if lang == "english": langCode = "en"
                if lang == "japanese": langCode = "ja"
        self.comicinfoXML = f"""<?xml version="1.0"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Title>{self.name}</Title>
  <Year>{self.info.date.year}</Year>
  <Month>{self.info.date.month}</Month>
  <Day>{self.info.date.day}</Day>
  <Writer>{string.capwords(self.info.artists)}</Writer>
  <Penciller>{string.capwords(self.info.artists)}</Penciller>
  <Inker>{string.capwords(self.info.artists)}</Inker>
  <Genre>{self.info.tags}</Genre>
  <Characters>{string.capwords(self.info.characters)}</Characters>
  <Locations>{self.info.parodies}</Locations>
  <Web>{self.url}</Web>
  <PageCount>{self.pages}</PageCount>
  <LanguageISO>{langCode}</LanguageISO>
</ComicInfo>
"""

    def __repr__(self):
        return '<Doujinshi: {0}>'.format(self.name)

    def show(self):
        table = [
            ["Doujinshi", self.name],
            ["Subtitle", self.info.subtitle],
            ["Characters", self.info.characters],
            ["Authors", self.info.artists],
            ["Languages", self.info.languages],
            ["Tags", self.info.tags],
            ["Parodies", self.info.parodies],
            ["URL", self.url],
            ["Pages", self.pages],
            ["Uploaded", self.info.date],
        ]
        logger.info(u'Print doujinshi information of {0}\n{1}'.format(self.id, tabulate(table)))

    def download(self):
        logger.info('Starting to download doujinshi: %s' % self.name)
        if self.downloader:
            download_queue = []

            if len(self.ext) != self.pages:
                logger.warning('Page count and ext count do not equal')

            for i in range(1, min(self.pages, len(self.ext)) + 1):
                download_queue.append('%s/%d/%d.%s' % (IMAGE_URL, int(self.img_id), i, self.ext[i-1]))

            self.downloader.download(download_queue, self.filename)

            with open(os.path.join(self.path, self.filename, 'ComicInfo.xml'), "w") as f:
                    f.write(self.comicinfoXML)

            '''
            for i in range(len(self.ext)):
                download_queue.append('%s/%d/%d.%s' % (IMAGE_URL, int(self.img_id), i+1, EXT_MAP[self.ext[i]]))
            '''

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
