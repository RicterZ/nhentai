import os

SCHEMA = os.getenv('NHENTAI_SCHEMA', 'http://')
# BASE_URL = 'nhentai.net'
BASE_URL = os.getenv('NHENTAI', 'nhentai.ricterz.me')

URL = '%s%s' % (SCHEMA, BASE_URL)
DETAIL_URL = '%s/g' % URL
SEARCH_URL = '%s/search/' % URL
IMAGE_URL = '%si.%s/galleries' % (SCHEMA, BASE_URL)
PROXY = {}
