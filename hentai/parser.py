import sys
import re
import requests
from bs4 import BeautifulSoup
from constant import DETAIL_URL
from hentai.logger import logger

def dojinshi_parser(id):
    logger.debug('Fetching dojinshi information')
    if not isinstance(id, (int, )) or (isinstance(id, (str, )) and not id.isdigit()):
        raise Exception('Dojinshi id(%s) is not valid' % str(id))
    id = int(id)
    dojinshi = dict()
    dojinshi['id'] = id
    url = '%s/%d/' % (DETAIL_URL, id)

    response = requests.get(url).content
    html = BeautifulSoup(response)
    dojinshi_info = html.find('div', attrs={'id': 'info'})

    title = dojinshi_info.find('h1').text
    subtitle = dojinshi_info.find('h2')

    dojinshi['name'] = title
    dojinshi['subtitle'] = subtitle.text if subtitle else ''

    dojinshi_cover = html.find('div', attrs={'id': 'cover'})
    img_id = re.search('/galleries/([\d]+)/cover\.(jpg|png)$', dojinshi_cover.a.img['src'])
    if not img_id:
        logger.critical('Tried yo get image id failed')
        sys.exit()
    dojinshi['img_id'] = img_id.group(1)
    dojinshi['ext'] = img_id.group(2)

    pages = 0
    for _ in dojinshi_info.find_all('div', class_=''):
        pages = re.search('([\d]+) pages', _.text)
        if pages:
            pages = pages.group(1)
            break
    dojinshi['pages'] = int(pages)
    return dojinshi


if __name__ == '__main__':
    print dojinshi_parser(32271)