# coding: utf-8
from __future__ import unicode_literals, print_function
from tabulate import tabulate
from bs4 import BeautifulSoup

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
    metadata = format_metadata(doujinshi_obj)

    if doujinshi_obj is not None:
        title = doujinshi_obj.name

        if sys.version_info < (3, 0):
            title = title.encode('utf-8')
    else:
        title = 'nHentai HTML Viewer'

    data = html.format(TITLE=title, IMAGES=image_html, SCRIPTS=js, STYLES=css, METADATA=metadata)
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
    scripts = readfile('viewer/mainscripts.js')
    element = '\n\
            <div class="gallery-favorite">\n\
                <div class="gallery" data-metadata="{METADATA}">\n\
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
            metadata = extract_metadata('./{}/index.html'.format(folder))
        else:
            metadata = ''
            continue

        image = files[0]  # 001.jpg or 001.png
        if folder is not None:
            title = folder.replace('_', ' ')
        else:
            title = 'nHentai HTML Viewer'

        image_html += element.format(METADATA=metadata, FOLDER=folder, IMAGE=image, TITLE=title)

    if image_html == '':
        logger.warning('None index.html found, --gen-main paused.')
        return
    try:
        data = main.format(STYLES=css, COUNT=count, PICTURE=image_html, SCRIPTS=scripts)
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


def signal_handler(signal, frame):
    logger.error('Ctrl-C signal received. Stopping...')
    exit(1)

def format_metadata(doujinshi_obj=None):
    metadata = readfile('viewer/metadata.html')

    if doujinshi_obj is not None:
        m_titleen = doujinshi_obj.name
        m_title = doujinshi_obj.info.subtitle
        m_id = str(doujinshi_obj.id)
        m_language = ''
        m_author = ''
        m_characters = ''
        m_tags = ''

        m_languagelist = doujinshi_obj.info.languages.split(', ')
        m_authorlist = doujinshi_obj.info.artists.split(', ')
        m_characterslist = doujinshi_obj.info.characters.split(', ')
        m_tagslist = doujinshi_obj.info.tags.split(', ')

        for language in m_languagelist:
            m_language += '\t\t<li>{}</li>\n'.format(language)
        for author in m_authorlist:
            m_author += '\t\t<li>{}</li>\n'.format(author)
        for characters in m_characterslist:
            m_characters += '\t\t<li>{}</li>\n'.format(characters)
        for tags in m_tagslist:
            m_tags += '\t\t<li>{}</li>\n'.format(tags)

        if sys.version_info < (3, 0):
            m_titleen = m_titleen.encode('utf-8')
            m_title = m_title.encode('utf-8')
            m_id = m_id.encode('utf-8')
            m_language = m_language.encode('utf-8')
            m_author = m_author.encode('utf-8')
            m_characters = m_characters.encode('utf-8')
            m_tags = m_tags.encode('utf-8')
    else:
        m_titleen = 'ERROR'
        m_title = 'ERROR'
        m_language = '\t\t<li>ERROR</li>\n'
        m_author = '\t\t<li>ERROR</li>\n'
        m_characters = '\t\t<li>ERROR</li>\n'
        m_tags = '\t\t<li>ERROR</li>\n'

    return metadata.format(M_TITLEEN=m_titleen, M_TITLE=m_title, M_ID=m_id, M_LANGUAGE=m_language, M_AUTHOR=m_author, M_CHARACTERS=m_characters, M_TAGS=m_tags)  

def generate_index(output_dir='./', doujinshi_list=None):
    if doujinshi_list is not None:
        for doujinshi_obj in doujinshi_list:
            if os.path.exists(os.path.join(output_dir, doujinshi_obj.filename)):
                generate_html(output_dir, doujinshi_obj)
            else:
                logger.warning('Folder {} does not exist, skipped'.format(doujinshi_obj.filename))
    else:
        logger.error('No doujinshi list detected')

def extract_metadata(indexpath):
    indexfile = open(indexpath, 'r', encoding='utf-8')
    indexcontent = indexfile.read()
    index = BeautifulSoup(indexcontent, 'html.parser')

    metadata = index.select('#metadata-id')[0].string + ' ' + index.select('#metadata-titleEN')[0].string

    for language in index.select('#metadata-language')[0].stripped_strings:
        metadata += ' ' + language
    for author in index.select('#metadata-author')[0].stripped_strings:
        metadata += ' ' + author
    for character in index.select('#metadata-characters')[0].stripped_strings:
        metadata += ' ' + character
    for tag in index.select('#metadata-tags')[0].stripped_strings:
        metadata += ' ' + tag

    return metadata.replace('"', '\'')
