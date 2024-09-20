# coding: utf-8
import os
import tempfile

from urllib.parse import urlparse
from platform import system


def get_nhentai_home() -> str:
    home = os.getenv('HOME', tempfile.gettempdir())

    if system() == 'Linux':
        xdgdat = os.getenv('XDG_DATA_HOME')
        if xdgdat and os.path.exists(os.path.join(xdgdat, 'nhentai')):
            return os.path.join(xdgdat, 'nhentai')
        if home and os.path.exists(os.path.join(home, '.nhentai')):
            return os.path.join(home, '.nhentai')
        if xdgdat:
            return os.path.join(xdgdat, 'nhentai')

    # Use old default path in other systems
    return os.path.join(home, '.nhentai')


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
IMAGE_URL_MIRRORS = [
    f'{urlparse(BASE_URL).scheme}://i3.{urlparse(BASE_URL).hostname}'
    f'{urlparse(BASE_URL).scheme}://i5.{urlparse(BASE_URL).hostname}'
    f'{urlparse(BASE_URL).scheme}://i7.{urlparse(BASE_URL).hostname}'
]

NHENTAI_HOME = get_nhentai_home()
NHENTAI_HISTORY = os.path.join(NHENTAI_HOME, 'history.sqlite3')
NHENTAI_CONFIG_FILE = os.path.join(NHENTAI_HOME, 'config.json')

__api_suspended_DETAIL_URL = f'{BASE_URL}/api/gallery'

CONFIG = {
    'proxy': {'http': '', 'https': ''},
    'cookie': '',
    'language': '',
    'template': '',
    'useragent': 'nhentai command line client (https://github.com/RicterZ/nhentai)',
    'max_filename': 85
}

LANGUAGE_ISO = {
    'english': 'en',
    'chinese': 'zh',
    'japanese': 'ja',
    'translated': 'translated'
}
