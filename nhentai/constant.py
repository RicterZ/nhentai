# coding: utf-8
from __future__ import unicode_literals, print_function
import os
import tempfile

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


BASE_URL = os.getenv('NHENTAI', 'https://nhentai.net')

__api_suspended_DETAIL_URL = '%s/api/gallery' % BASE_URL

DETAIL_URL = '%s/g' % BASE_URL
SEARCH_URL = '%s/api/galleries/search' % BASE_URL


TAG_API_URL = '%s/api/galleries/tagged' % BASE_URL
LOGIN_URL = '%s/login/' % BASE_URL
CHALLENGE_URL = '%s/challenge' % BASE_URL
FAV_URL = '%s/favorites/' % BASE_URL

u = urlparse(BASE_URL)
IMAGE_URL = '%s://i.%s/galleries' % (u.scheme, u.hostname)

NHENTAI_HOME = os.path.join(os.getenv('HOME', tempfile.gettempdir()), '.nhentai')
NHENTAI_PROXY = os.path.join(NHENTAI_HOME, 'proxy')
NHENTAI_COOKIE = os.path.join(NHENTAI_HOME, 'cookie')
NHENTAI_LANGUAGE = os.path.join(NHENTAI_HOME, 'language')
NHENTAI_HISTORY = os.path.join(NHENTAI_HOME, 'history.sqlite3')

PROXY = {}

COOKIE = ''
LANGUAGE = ''
