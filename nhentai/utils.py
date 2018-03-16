# coding: utf-8
from __future__ import unicode_literals, print_function

import os
import string
from nhentai.logger import logger


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton(str('SingletonMeta'), (object,), {})):
    pass


def urlparse(url):
    try:
        from urlparse import urlparse
    except ImportError:
        from urllib.parse import urlparse

    return urlparse(url)


def generate_html(output_dir='.', doujinshi_obj=None):
    image_html = ''
    previous = ''

    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, format_filename('%s-%s' % (doujinshi_obj.id,
                                                                            doujinshi_obj.name[:200])))
    else:
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    for index, image in enumerate(file_list):
        if not os.path.splitext(image)[1] in ('.jpg', '.png'):
            continue

        try:
            next_ = file_list[file_list.index(image) + 1]
        except IndexError:
            next_ = ''

        image_html += '<img src="{0}" class="image-item {1}" attr-prev="{2}" attr-next="{3}">\n'\
            .format(image, 'current' if index == 0 else '', previous, next_)
        previous = image

    with open(os.path.join(os.path.dirname(__file__), 'doujinshi.html'), 'r') as template:
        html = template.read()

    if doujinshi_obj is not None:
        title = doujinshi_obj.name
    else:
        title = 'nHentai HTML Viewer'

    data = html.format(TITLE=title, IMAGES=image_html)
    with open(os.path.join(doujinshi_dir, 'index.html'), 'w') as f:
        f.write(data)

    logger.log(15, 'HTML Viewer has been write to \'{0}\''.format(os.path.join(doujinshi_dir, 'index.html')))


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename
