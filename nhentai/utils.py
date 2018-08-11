# coding: utf-8
from __future__ import unicode_literals, print_function

import os
import string
import zipfile
import shutil
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

def readfile(path):
    loc = os.path.dirname(__file__)

    with open(os.path.join(loc, path), 'r') as file:
        return file.read()

def generate_html(output_dir='.', doujinshi_obj=None):
    image_html = ''

    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, format_filename('%s-%s' % (doujinshi_obj.id,
                                                                            str(doujinshi_obj.name[:200]))))
    else:
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    for image in file_list:
        if not os.path.splitext(image)[1] in ('.jpg', '.png'):
            continue

        image_html += '<img src="{0}" class="image-item"/>\n'\
            .format(image)

    html = readfile('viewer/index.html')
    css = readfile('viewer/styles.css')
    js = readfile('viewer/scripts.js')

    if doujinshi_obj is not None:
        title = doujinshi_obj.name
    else:
        title = 'nHentai HTML Viewer'

    data = html.format(TITLE=title, IMAGES=image_html, SCRIPTS=js, STYLES=css)
    with open(os.path.join(doujinshi_dir, 'index.html'), 'w') as f:
        f.write(data)

    logger.log(15, 'HTML Viewer has been write to \'{0}\''.format(os.path.join(doujinshi_dir, 'index.html')))


def generate_cbz(output_dir='.', doujinshi_obj=None):
    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, format_filename('%s-%s' % (doujinshi_obj.id,
                                                                            str(doujinshi_obj.name[:200]))))    
        cbz_filename = os.path.join(output_dir, format_filename('%s-%s.cbz' % (doujinshi_obj.id,
                                                                            str(doujinshi_obj.name[:200]))))
    else:
        cbz_filename = './doujinshi.cbz'
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()
    
    with zipfile.ZipFile(cbz_filename, 'w') as cbz_pf:
        for image in file_list:
            image_path = os.path.join(doujinshi_dir, image)
            cbz_pf.write(image_path, image)
            
    shutil.rmtree(doujinshi_dir, ignore_errors=True)
    logger.log(15, 'Comic Book CBZ file has been write to \'{0}\''.format(doujinshi_dir))







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
