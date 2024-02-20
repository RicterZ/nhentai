# coding: utf-8
import os
import tempfile

from urllib.parse import urlparse


DEBUG = os.getenv('DEBUG', False)
BASE_URL = os.getenv('NHENTAI', 'https://nhentai.net')

DETAIL_URL = f'{BASE_URL}/g'
LEGACY_SEARCH_URL = f'{BASE_URL}/search/'
SEARCH_URL = f'{BASE_URL}/api/galleries/search'
ARTIST_URL = f'{BASE_URL}/artist/'

TAG_API_URL = f'{BASE_URL}/api/galleries/tagged'
LOGIN_URL = f'{BASE_URL}/login/'
CHALLENGE_URL = f'{BASE_URL}/challenge'
FAV_URL = f'{BASE_URL}/favorites/'


IMAGE_URL = f'{urlparse(BASE_URL).scheme}://i.{urlparse(BASE_URL).hostname}/galleries'

NHENTAI_HOME = os.path.join(os.getenv('HOME', tempfile.gettempdir()), '.nhentai')
NHENTAI_HISTORY = os.path.join(NHENTAI_HOME, 'history.sqlite3')
NHENTAI_CONFIG_FILE = os.path.join(NHENTAI_HOME, 'config.json')

__api_suspended_DETAIL_URL = f'{BASE_URL}/api/gallery'

CONFIG = {
    'proxy': {'http': '', 'https': ''},
    'cookie': '',
    'language': '',
    'template': '',
    'useragent': 'nhentai command line client (https://github.com/RicterZ/nhentai)'
}

LANGUAGE_ISO = {
    'english': 'en',
    'chinese': 'zh',
    'japanese': 'ja',
    'translated': 'translated'
}
