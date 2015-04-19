import re
import requests
from bs4 import BeautifulSoup
from constant import DETAIL_URL


dojinshi_fields = ['Artists:']


def dojinshi_parser(id):
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