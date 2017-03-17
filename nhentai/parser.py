# coding: utf-8
from __future__ import unicode_literals, print_function

from bs4 import BeautifulSoup
import re
import requests
from tabulate import tabulate

import nhentai.constant as constant
from nhentai.logger import logger


def request(method, url, **kwargs):
    if not hasattr(requests, method):
        raise AttributeError('\'requests\' object has no attribute \'{0}\''.format(method))

    return requests.__dict__[method](url, proxies=constant.PROXY, verify=False, **kwargs)


def doujinshi_parser(id_):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception('Doujinshi id({0}) is not valid'.format(id_))

    id_ = int(id_)
    logger.log(15, 'Fetching doujinshi information of id {0}'.format(id_))
    doujinshi = dict()
    doujinshi['id'] = id_
    url = '{0}/{1}/'.format(constant.DETAIL_URL, id_)

    try:
        response = request('get', url).content
    except Exception as e:
        logger.critical(str(e))
        exit(1)

    html = BeautifulSoup(response, 'html.parser')
    doujinshi_info = html.find('div', attrs={'id': 'info'})

    title = doujinshi_info.find('h1').text
    subtitle = doujinshi_info.find('h2')

    doujinshi['name'] = title
    doujinshi['subtitle'] = subtitle.text if subtitle else ''

    doujinshi_cover = html.find('div', attrs={'id': 'cover'})
    img_id = re.search('/galleries/([\d]+)/cover\.(jpg|png)$', doujinshi_cover.a.img.attrs['data-src'])
    if not img_id:
        logger.critical('Tried yo get image id failed')
        exit(1)

    doujinshi['img_id'] = img_id.group(1)
    doujinshi['ext'] = img_id.group(2)

    pages = 0
    for _ in doujinshi_info.find_all('div', class_=''):
        pages = re.search('([\d]+) pages', _.text)
        if pages:
            pages = pages.group(1)
            break
    doujinshi['pages'] = int(pages)

    # gain information of the doujinshi
    information_fields = doujinshi_info.find_all('div', attrs={'class': 'field-name'})
    needed_fields = ['Characters', 'Artists', 'Language', 'Tags']
    for field in information_fields:
        field_name = field.contents[0].strip().strip(':')
        if field_name in needed_fields:
            data = [sub_field.contents[0].strip() for sub_field in
                    field.find_all('a', attrs={'class': 'tag'})]
            doujinshi[field_name.lower()] = ', '.join(data)

    return doujinshi


def search_parser(keyword, page):
    logger.debug('Searching doujinshis of keyword {0}'.format(keyword))
    result = []
    try:
        response = request('get', url=constant.SEARCH_URL, params={'q': keyword, 'page': page}).content
    except requests.ConnectionError as e:
        logger.critical(e)
        logger.warn('If you are in China, please configure the proxy to fu*k GFW.')
        exit(1)

    html = BeautifulSoup(response, 'html.parser')
    doujinshi_search_result = html.find_all('div', attrs={'class': 'gallery'})
    for doujinshi in doujinshi_search_result:
        doujinshi_container = doujinshi.find('div', attrs={'class': 'caption'})
        title = doujinshi_container.text.strip()
        title = (title[:85] + '..') if len(title) > 85 else title
        id_ = re.search('/g/(\d+)/', doujinshi.a['href']).group(1)
        result.append({'id': id_, 'title': title})
    if not result:
        logger.warn('Not found anything of keyword {}'.format(keyword))

    return result


def print_doujinshi(doujinshi_list):
    if not doujinshi_list:
        return
    doujinshi_list = [(i['id'], i['title']) for i in doujinshi_list]
    headers = ['id', 'doujinshi']
    logger.info('Search Result\n' +
                tabulate(tabular_data=doujinshi_list, headers=headers, tablefmt='rst'))

if __name__ == '__main__':
    print(doujinshi_parser("32271"))
