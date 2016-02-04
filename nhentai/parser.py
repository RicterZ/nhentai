# coding: utf-8
from __future__ import print_function
import sys
import re
import requests
from bs4 import BeautifulSoup
import constant
from logger import logger
from tabulate import tabulate


def request(method, url, **kwargs):
    if not hasattr(requests, method):
        raise AttributeError('\'requests\' object has no attribute \'{}\''.format(method))

    return requests.__dict__[method](url, proxies=constant.PROXY, **kwargs)


def doujinshi_parser(id):
    if not isinstance(id, (int, )) and (isinstance(id, (str, )) and not id.isdigit()):
        raise Exception('Doujinshi id(%s) is not valid' % str(id))
    id = int(id)
    logger.debug('Fetching doujinshi information of id %d' % id)
    doujinshi = dict()
    doujinshi['id'] = id
    url = '%s/%d/' % (constant.DETAIL_URL, id)

    try:
        response = request('get', url).content
    except Exception as e:
        logger.critical('%s%s' % tuple(e.message))
        sys.exit()

    html = BeautifulSoup(response)
    doujinshi_info = html.find('div', attrs={'id': 'info'})

    title = doujinshi_info.find('h1').text
    subtitle = doujinshi_info.find('h2')

    doujinshi['name'] = title
    doujinshi['subtitle'] = subtitle.text if subtitle else ''

    doujinshi_cover = html.find('div', attrs={'id': 'cover'})
    img_id = re.search('/galleries/([\d]+)/cover\.(jpg|png)$', doujinshi_cover.a.img['src'])
    if not img_id:
        logger.critical('Tried yo get image id failed')
        sys.exit()
    doujinshi['img_id'] = img_id.group(1)
    doujinshi['ext'] = img_id.group(2)

    pages = 0
    for _ in doujinshi_info.find_all('div', class_=''):
        pages = re.search('([\d]+) pages', _.text)
        if pages:
            pages = pages.group(1)
            break
    doujinshi['pages'] = int(pages)
    return doujinshi


def search_parser(keyword, page):
    logger.debug('Searching doujinshis of keyword %s' % keyword)
    result = []
    try:
        response = request('get', url=constant.SEARCH_URL, params={'q': keyword, 'page': page}).content
    except requests.ConnectionError as e:
        logger.critical(e)
        logger.warn('If you are in China, please configure the proxy to fu*k GFW.')
        raise SystemExit

    html = BeautifulSoup(response)
    doujinshi_search_result = html.find_all('div', attrs={'class': 'gallery'})
    for doujinshi in doujinshi_search_result:
        doujinshi_container = doujinshi.find('div', attrs={'class': 'caption'})
        title = doujinshi_container.text.strip()
        title = (title[:85] + '..') if len(title) > 85 else title
        id_ = re.search('/g/(\d+)/', doujinshi.a['href']).group(1)
        result.append({'id': id_, 'title': title})
    return result


def print_doujinshi(doujinshi_list):
    if not doujinshi_list:
        return
    doujinshi_list = [i.values() for i in doujinshi_list]
    headers = ['id', 'doujinshi']
    logger.info('Search Result\n' +
                tabulate(tabular_data=doujinshi_list, headers=headers, tablefmt='rst'))

if __name__ == '__main__':
    print(doujinshi_parser("32271"))
