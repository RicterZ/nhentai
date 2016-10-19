# coding: utf-8
from __future__ import unicode_literals, print_function
import os
from nhentai.utils import urlparse

BASE_URL = os.getenv('NHENTAI', 'https://nhentai.net')

DETAIL_URL = '%s/g' % BASE_URL
SEARCH_URL = '%s/search/' % BASE_URL

u = urlparse(BASE_URL)
IMAGE_URL = '%s://i.%s/galleries' % (u.scheme, u.hostname)

PROXY = {}
