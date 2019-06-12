# coding: utf-8
from __future__ import unicode_literals, print_function

import sys
import re
import os
import string
import zipfile
import shutil
import requests

from nhentai import constant
from nhentai.logger import logger


def request(method, url, **kwargs):
    session = requests.Session()
    session.headers.update({
        'Referer': constant.LOGIN_URL,
        'User-Agent': 'nhentai command line client (https://github.com/RicterZ/nhentai)',
        'Cookie': constant.COOKIE
    })
    return getattr(session, method)(url, proxies=constant.PROXY, verify=False, **kwargs)


def check_cookie():
    response = request('get', constant.BASE_URL).text
    username = re.findall('"/users/\d+/(.*?)"', response)
    if not username:
        logger.error('Cannot get your username, please check your cookie or use `nhentai --cookie` to set your cookie')
    else:
        logger.info('Login successfully! Your username: {}'.format(username[0]))


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
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
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
        if sys.version_info < (3, 0):
            title = title.encode('utf-8')
    else:
        title = 'nHentai HTML Viewer'

    data = html.format(TITLE=title, IMAGES=image_html, SCRIPTS=js, STYLES=css)
    try:
        if sys.version_info < (3, 0):
            with open(os.path.join(doujinshi_dir, 'index.html'), 'w') as f:
                f.write(data)
        else:
            with open(os.path.join(doujinshi_dir, 'index.html'), 'wb') as f:
                f.write(data.encode('utf-8'))

        logger.log(15, 'HTML Viewer has been write to \'{0}\''.format(os.path.join(doujinshi_dir, 'index.html')))
    except Exception as e:
        logger.warning('Writen HTML Viewer failed ({})'.format(str(e)))


def generate_main_html(output_dir='./'):
    """
    Generate a main html to show all the contain doujinshi.
    With a link to their `index.html`.
    Default output folder will be the CLI path.
    """

    count = 0
    image_html = ''
    main = readfile('viewer/main.html')
    css = readfile('viewer/main.css')
    element = '\n\
            <div class="gallery-favorite">\n\
                <div class="gallery">\n\
                    <a href="./{FOLDER}/index.html" class="cover" style="padding:0 0 141.6% 0"><img\n\
                            src="./{FOLDER}/{IMAGE}" />\n\
                        <div class="caption">{TITLE}</div>\n\
                    </a>\n\
                </div>\n\
            </div>\n'

    os.chdir(output_dir)
    doujinshi_dirs = next(os.walk('.'))[1]

    for folder in doujinshi_dirs:

        files = os.listdir(folder)
        files.sort()

        if 'index.html' in files:
            count += 1
            logger.info('Add doujinshi \'{}\''.format(folder))
        else:
            continue

        image = files[0]  # 001.jpg or 001.png
        if folder is not None:
            title = folder.replace('_', ' ')
        else:
            title = 'nHentai HTML Viewer'

        image_html += element.format(FOLDER=folder, IMAGE=image, TITLE=title)

    if image_html == '':
        logger.warning('None index.html found, --gen-main paused.')
        return
    try:
        data = main.format(STYLES=css, COUNT=count, PICTURE=image_html)
        if sys.version_info < (3, 0):
            with open('./main.html', 'w') as f:
                f.write(data)
        else:
            with open('./main.html', 'wb') as f:
                f.write(data.encode('utf-8'))
        logger.log(
            15, 'Main Viewer has been write to \'{0}main.html\''.format(output_dir))
    except Exception as e:
        logger.warning('Writen Main Viewer failed ({})'.format(str(e)))


def generate_cbz(output_dir='.', doujinshi_obj=None, rm_origin_dir=False):
    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
        cbz_filename = os.path.join(os.path.join(doujinshi_dir, '..'), '%s.cbz' % doujinshi_obj.id)
    else:
        cbz_filename = './doujinshi.cbz'
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    logger.info('Writing CBZ file to path: {}'.format(cbz_filename))
    with zipfile.ZipFile(cbz_filename, 'w') as cbz_pf:
        for image in file_list:
            image_path = os.path.join(doujinshi_dir, image)
            cbz_pf.write(image_path, image)

    if rm_origin_dir:
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
    valid_chars = "-_.()[] %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    if len(filename) > 100:
        filename = filename[:100] + '...]'

    # Remove [] from filename
    filename = filename.replace('[]', '')
    return filename
