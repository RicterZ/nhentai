# coding: utf-8
from __future__ import unicode_literals, print_function

import sys
import re
import os
import string
import zipfile
import shutil
import requests
import sqlite3

from nhentai import constant
from nhentai.logger import logger
from nhentai.serializer import serialize_json, serialize_comicxml, set_js_database


def request(method, url, **kwargs):
    session = requests.Session()
    session.headers.update({
        'Referer': constant.LOGIN_URL,
        'User-Agent': 'nhentai command line client (https://github.com/RicterZ/nhentai)',
        'Cookie': constant.CONFIG['cookie']
    })
    return getattr(session, method)(url, proxies=constant.CONFIG['proxy'], verify=False, **kwargs)


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
        serialize_json(doujinshi_obj, doujinshi_dir)
        name = doujinshi_obj.name
        if sys.version_info < (3, 0):
            name = doujinshi_obj.name.encode('utf-8')
    else:
        name = {'title': 'nHentai HTML Viewer'}

    data = html.format(TITLE=name, IMAGES=image_html, SCRIPTS=js, STYLES=css)
    try:
        if sys.version_info < (3, 0):
            with open(os.path.join(doujinshi_dir, 'index.html'), 'w') as f:
                f.write(data)
        else:
            with open(os.path.join(doujinshi_dir, 'index.html'), 'wb') as f:
                f.write(data.encode('utf-8'))

        logger.log(15, 'HTML Viewer has been written to \'{0}\''.format(os.path.join(doujinshi_dir, 'index.html')))
    except Exception as e:
        logger.warning('Writing HTML Viewer failed ({})'.format(str(e)))


def generate_main_html(output_dir='./'):
    """
    Generate a main html to show all the contain doujinshi.
    With a link to their `index.html`.
    Default output folder will be the CLI path.
    """

    image_html = ''

    main = readfile('viewer/main.html')
    css = readfile('viewer/main.css')
    js = readfile('viewer/main.js')

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
        logger.warning('No index.html found, --gen-main paused.')
        return
    try:
        data = main.format(STYLES=css, SCRIPTS=js, PICTURE=image_html)
        if sys.version_info < (3, 0):
            with open('./main.html', 'w') as f:
                f.write(data)
        else:
            with open('./main.html', 'wb') as f:
                f.write(data.encode('utf-8'))
        shutil.copy(os.path.dirname(__file__)+'/viewer/logo.png', './')
        set_js_database()
        logger.log(
            15, 'Main Viewer has been written to \'{0}main.html\''.format(output_dir))
    except Exception as e:
        logger.warning('Writing Main Viewer failed ({})'.format(str(e)))


def generate_cbz(output_dir='.', doujinshi_obj=None, rm_origin_dir=False, write_comic_info=False):
    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
        if write_comic_info:
            serialize_comicxml(doujinshi_obj, doujinshi_dir)
        cbz_filename = os.path.join(os.path.join(doujinshi_dir, '..'), '{}.cbz'.format(doujinshi_obj.filename))
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

    logger.log(15, 'Comic Book CBZ file has been written to \'{0}\''.format(doujinshi_dir))


def generate_pdf(output_dir='.', doujinshi_obj=None, rm_origin_dir=False):
    try:
        import img2pdf
    except ImportError:
        logger.error("Please install img2pdf package by using pip.")

    """Write images to a PDF file using img2pdf."""
    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
        pdf_filename = os.path.join(
            os.path.join(doujinshi_dir, '..'),
            '{}.pdf'.format(doujinshi_obj.filename)
        )
    else:
        pdf_filename = './doujinshi.pdf'
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    logger.info('Writing PDF file to path: {}'.format(pdf_filename))
    with open(pdf_filename, 'wb') as pdf_f:
        full_path_list = (
            [os.path.join(doujinshi_dir, image) for image in file_list]
        )
        pdf_f.write(img2pdf.convert(full_path_list))

    if rm_origin_dir:
        shutil.rmtree(doujinshi_dir, ignore_errors=True)

    logger.log(15, 'PDF file has been written to \'{0}\''.format(doujinshi_dir))


def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.

Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.

"""
    # maybe you can use `--format` to select a suitable filename
    valid_chars = "-_.()[] %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    if len(filename) > 100:
        filename = filename[:100] + '...]'

    # Remove [] from filename
    filename = filename.replace('[]', '').strip()
    return filename


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Stopping...')
    exit(1)


def paging(page_string):
    # 1,3-5,14 -> [1, 3, 4, 5, 14]
    if not page_string:
        return []

    page_list = []
    for i in page_string.split(','):
        if '-' in i:
            start, end = i.split('-')
            if not (start.isdigit() and end.isdigit()):
                raise Exception('Invalid page number')
            page_list.extend(list(range(int(start), int(end)+1)))
        else:
            if not i.isdigit():
                raise Exception('Invalid page number')
            page_list.append(int(i))

    return page_list


class DB(object):
    conn = None
    cur = None

    def __enter__(self):
        self.conn = sqlite3.connect(constant.NHENTAI_HISTORY)
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS download_history (id text)')
        self.conn.commit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def clean_all(self):
        self.cur.execute('DELETE FROM download_history WHERE 1')
        self.conn.commit()

    def add_one(self, data):
        self.cur.execute('INSERT INTO download_history VALUES (?)', [data])
        self.conn.commit()

    def get_all(self):
        data = self.cur.execute('SELECT id FROM download_history')
        return [i[0] for i in data]
