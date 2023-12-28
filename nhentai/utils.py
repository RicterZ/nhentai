# coding: utf-8

import sys
import re
import os
import zipfile
import shutil
import requests
import sqlite3

from nhentai import constant
from nhentai.logger import logger
from nhentai.serializer import serialize_json, serialize_comic_xml, set_js_database


MAX_FIELD_LENGTH = 100


def request(method, url, **kwargs):
    session = requests.Session()
    session.headers.update({
        'Referer': constant.LOGIN_URL,
        'User-Agent': constant.CONFIG['useragent'],
        'Cookie': constant.CONFIG['cookie']
    })

    if not kwargs.get('proxies', None):
        kwargs['proxies'] = constant.CONFIG['proxy']

    return getattr(session, method)(url, verify=False, **kwargs)


def check_cookie():
    response = request('get', constant.BASE_URL)
    if response.status_code == 403 and 'Just a moment...' in response.text:
        logger.error('Blocked by Cloudflare captcha, please set your cookie and useragent')
        sys.exit(1)

    username = re.findall('"/users/[0-9]+/(.*?)"', response.text)
    if not username:
        logger.warning('Cannot get your username, please check your cookie or use `nhentai --cookie` to set your cookie')
    else:
        logger.log(16, f'Login successfully! Your username: {username[0]}')


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton(str('SingletonMeta'), (object,), {})):
    pass


def readfile(path):
    loc = os.path.dirname(__file__)

    with open(os.path.join(loc, path), 'r') as file:
        return file.read()


def generate_html(output_dir='.', doujinshi_obj=None, template='default'):
    image_html = ''

    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
    else:
        doujinshi_dir = '.'

    if not os.path.exists(doujinshi_dir):
        logger.warning(f'Path "{doujinshi_dir}" does not exist, creating.')
        try:
            os.makedirs(doujinshi_dir)
        except EnvironmentError as e:
            logger.critical(e)

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    for image in file_list:
        if not os.path.splitext(image)[1] in ('.jpg', '.png'):
            continue
        image_html += f'<img src="{image}" class="image-item"/>\n'

    html = readfile(f'viewer/{template}/index.html')
    css = readfile(f'viewer/{template}/styles.css')
    js = readfile(f'viewer/{template}/scripts.js')

    if doujinshi_obj is not None:
        serialize_json(doujinshi_obj, doujinshi_dir)
        name = doujinshi_obj.name
    else:
        name = {'title': 'nHentai HTML Viewer'}

    data = html.format(TITLE=name, IMAGES=image_html, SCRIPTS=js, STYLES=css)
    try:
        with open(os.path.join(doujinshi_dir, 'index.html'), 'wb') as f:
            f.write(data.encode('utf-8'))

        logger.log(16, f'HTML Viewer has been written to "{os.path.join(doujinshi_dir, "index.html")}"')
    except Exception as e:
        logger.warning(f'Writing HTML Viewer failed ({e})')


def generate_main_html(output_dir='./'):
    """
    Generate a main html to show all the contains doujinshi.
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
            logger.info(f'Add doujinshi "{folder}"')
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
        with open('./main.html', 'wb') as f:
            f.write(data.encode('utf-8'))
        shutil.copy(os.path.dirname(__file__) + '/viewer/logo.png', './')
        set_js_database()
        logger.log(16, f'Main Viewer has been written to "{output_dir}main.html"')
    except Exception as e:
        logger.warning(f'Writing Main Viewer failed ({e})')


def generate_cbz(output_dir='.', doujinshi_obj=None, rm_origin_dir=False, write_comic_info=True, move_to_folder=False):
    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
        if write_comic_info:
            serialize_comic_xml(doujinshi_obj, doujinshi_dir)
        cbz_filename = os.path.join(os.path.join(doujinshi_dir, '..'), f'{doujinshi_obj.filename}.cbz')
    else:
        cbz_filename = './doujinshi.cbz'
        doujinshi_dir = '.'

    file_list = os.listdir(doujinshi_dir)
    file_list.sort()

    logger.info(f'Writing CBZ file to path: {cbz_filename}')
    with zipfile.ZipFile(cbz_filename, 'w') as cbz_pf:
        for image in file_list:
            image_path = os.path.join(doujinshi_dir, image)
            cbz_pf.write(image_path, image)

    if rm_origin_dir:
        shutil.rmtree(doujinshi_dir, ignore_errors=True)

    if move_to_folder:
            for filename in os.listdir(doujinshi_dir):
                file_path = os.path.join(doujinshi_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")

            shutil.move(cbz_filename, doujinshi_dir)

    logger.log(16, f'Comic Book CBZ file has been written to "{doujinshi_dir}"')


def generate_pdf(output_dir='.', doujinshi_obj=None, rm_origin_dir=False, move_to_folder=False):
    try:
        import img2pdf

        """Write images to a PDF file using img2pdf."""
        if doujinshi_obj is not None:
            doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
            pdf_filename = os.path.join(
                os.path.join(doujinshi_dir, '..'),
                f'{doujinshi_obj.filename}.pdf'
            )
        else:
            pdf_filename = './doujinshi.pdf'
            doujinshi_dir = '.'

        file_list = os.listdir(doujinshi_dir)
        file_list.sort()

        logger.info(f'Writing PDF file to path: {pdf_filename}')
        with open(pdf_filename, 'wb') as pdf_f:
            full_path_list = (
                [os.path.join(doujinshi_dir, image) for image in file_list]
            )
            pdf_f.write(img2pdf.convert(full_path_list))

        if rm_origin_dir:
            shutil.rmtree(doujinshi_dir, ignore_errors=True)

        if move_to_folder:
            for filename in os.listdir(doujinshi_dir):
                file_path = os.path.join(doujinshi_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file: {e}")

            shutil.move(pdf_filename, doujinshi_dir)

        logger.log(16, f'PDF file has been written to "{doujinshi_dir}"')

    except ImportError:
        logger.error("Please install img2pdf package by using pip.")


def format_filename(s, length=MAX_FIELD_LENGTH, _truncate_only=False):
    """
    It used to be a whitelist approach allowed only alphabet and a part of symbols.
    but most doujinshi's names include Japanese 2-byte characters and these was rejected.
    so it is using blacklist approach now.
    if filename include forbidden characters (\'/:,;*?"<>|) ,it replace space character(' '). 
    """
    # maybe you can use `--format` to select a suitable filename

    if not _truncate_only:
        ban_chars = '\\\'/:,;*?"<>|\t\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b'
        filename = s.translate(str.maketrans(ban_chars, ' ' * len(ban_chars))).strip()
        filename = ' '.join(filename.split())

        while filename.endswith('.'):
            filename = filename[:-1]
    else:
        filename = s

    # limit `length` chars
    if len(filename) >= length:
        filename = filename[:length - 1] + u'…'

    # Remove [] from filename
    filename = filename.replace('[]', '').strip()
    return filename


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Stopping...')
    sys.exit(1)


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
            page_list.extend(list(range(int(start), int(end) + 1)))
        else:
            if not i.isdigit():
                raise Exception('Invalid page number')
            page_list.append(int(i))

    return page_list


def generate_metadata_file(output_dir, table, doujinshi_obj=None):
    logger.info('Writing Metadata Info')

    if doujinshi_obj is not None:
        doujinshi_dir = os.path.join(output_dir, doujinshi_obj.filename)
    else:
        doujinshi_dir = '.'

    logger.info(doujinshi_dir)

    f = open(os.path.join(doujinshi_dir, 'info.txt'), 'w', encoding='utf-8')

    fields = ['TITLE', 'ORIGINAL TITLE', 'AUTHOR', 'ARTIST', 'GROUPS', 'CIRCLE', 'SCANLATOR',
              'TRANSLATOR', 'PUBLISHER', 'DESCRIPTION', 'STATUS', 'CHAPTERS', 'PAGES',
              'TAGS', 'TYPE', 'LANGUAGE', 'RELEASED', 'READING DIRECTION', 'CHARACTERS',
              'SERIES', 'PARODY', 'URL']
    special_fields = ['PARODY', 'TITLE', 'ORIGINAL TITLE', 'CHARACTERS', 'AUTHOR', 'GROUPS',
                      'LANGUAGE', 'TAGS', 'URL', 'PAGES']

    for i in range(len(fields)):
        f.write(f'{fields[i]}: ')
        if fields[i] in special_fields:
            f.write(str(table[special_fields.index(fields[i])][1]))
        f.write('\n')

    f.close()


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
