import os

BASE_URL = os.getenv('NHENTAI', 'https://nhentai.net')

DETAIL_URL = '%s/g' % BASE_URL
SEARCH_URL = '%s/search/' % BASE_URL
IMAGE_URL = 'https://i.%s/galleries' % BASE_URL

PROXY = {}
