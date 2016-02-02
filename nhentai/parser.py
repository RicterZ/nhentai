# coding: utf-8
from __future__ import print_function
import sys
import re
import requests
from bs4 import BeautifulSoup
from constant import DETAIL_URL, SEARCH_URL
from logger import logger
from tabulate import tabulate


def dojinshi_parser(id):
    if not isinstance(id, (int, )) and (isinstance(id, (str, )) and not id.isdigit()):
        raise Exception('Dojinshi id(%s) is not valid' % str(id))
    id = int(id)
    logger.debug('Fetching dojinshi information of id %d' % id)
    dojinshi = dict()
    dojinshi['id'] = id
    url = '%s/%d/' % (DETAIL_URL, id)

    try:
        response = requests.get(url).content
    except Exception as e:
        logger.critical('%s%s' % tuple(e.message))
        sys.exit()

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


def search_parser(keyword, page):
    logger.debug('Searching dojinshis of keyword %s' % keyword)
    result = []
    response = requests.get(SEARCH_URL, params={'q': keyword, 'page': page}).content
    html = BeautifulSoup(response)
    dojinshi_search_result = html.find_all('div', attrs={'class': 'gallery'})
    for dojinshi in dojinshi_search_result:
        dojinshi_container = dojinshi.find('div', attrs={'class': 'caption'})
        title = dojinshi_container.text.strip()
        title = (title[:85] + '..') if len(title) > 85 else title
        id_ = re.search('/g/(\d+)/', dojinshi.a['href']).group(1)
        result.append({'id': id_, 'title': title})
    return result


def print_dojinshi(dojinshi_list):
    if not dojinshi_list:
        return
    dojinshi_list = [i.values() for i in dojinshi_list]
    headers = ['id', 'dojinshi']
    logger.info('Search Result\n' +
                tabulate(tabular_data=dojinshi_list, headers=headers, tablefmt='rst'))

if __name__ == '__main__':
    print(dojinshi_parser("32271"))
