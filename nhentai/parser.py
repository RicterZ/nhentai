# coding: utf-8
from __future__ import unicode_literals, print_function

import os
import re
import threadpool
import requests
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

import nhentai.constant as constant
from nhentai.logger import logger


session = requests.Session()
session.headers.update({
    'Referer': constant.LOGIN_URL,
    'User-Agent': 'nhentai command line client (https://github.com/RicterZ/nhentai)',
})


def request(method, url, **kwargs):
    global session
    if not hasattr(session, method):
        raise AttributeError('\'requests.Session\' object has no attribute \'{0}\''.format(method))

    session.headers.update({'Cookie': constant.COOKIE})
    return getattr(session, method)(url, proxies=constant.PROXY, verify=False, **kwargs)


def _get_csrf_token(content):
    html = BeautifulSoup(content, 'html.parser')
    csrf_token_elem = html.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    if not csrf_token_elem:
        raise Exception('Cannot find csrf token to login')
    return csrf_token_elem.attrs['value']


def login(username, password):
    logger.warning('This feature is deprecated, please use --cookie to set your cookie.')
    csrf_token = _get_csrf_token(request('get', url=constant.LOGIN_URL).text)
    if os.getenv('DEBUG'):
        logger.info('Getting CSRF token ...')

    if os.getenv('DEBUG'):
        logger.info('CSRF token is {}'.format(csrf_token))

    login_dict = {
        'csrfmiddlewaretoken': csrf_token,
        'username_or_email': username,
        'password': password,
    }
    resp = request('post', url=constant.LOGIN_URL, data=login_dict)

    if 'You\'re loading pages way too quickly.' in resp.text or 'Really, slow down' in resp.text:
        csrf_token = _get_csrf_token(resp.text)
        resp = request('post', url=resp.url, data={'csrfmiddlewaretoken': csrf_token, 'next': '/'})

    if 'Invalid username/email or password' in resp.text:
        logger.error('Login failed, please check your username and password')
        exit(1)

    if 'You\'re loading pages way too quickly.' in resp.text or 'Really, slow down' in resp.text:
        logger.error('Using nhentai --cookie \'YOUR_COOKIE_HERE\' to save your Cookie.')
        exit(2)


def favorites_parser():
    html = BeautifulSoup(request('get', constant.FAV_URL).content, 'html.parser')
    count = html.find('span', attrs={'class': 'count'})
    if not count:
        logger.error("Can't get your number of favorited doujins. Did the login failed?")
        return []

    count = int(count.text.strip('(').strip(')').replace(',', ''))
    if count == 0:
        logger.warning('No favorites found')
        return []
    pages = int(count / 25)

    if pages:
        pages += 1 if count % (25 * pages) else 0
    else:
        pages = 1

    logger.info('You have %d favorites in %d pages.' % (count, pages))

    if os.getenv('DEBUG'):
        pages = 1

    ret = []
    doujinshi_id = re.compile('data-id="([\d]+)"')

    for page in range(1, pages + 1):
        try:
            logger.info('Getting doujinshi ids of page %d' % page)
            resp = request('get', constant.FAV_URL + '?page=%d' % page).text
            ids = doujinshi_id.findall(resp)
            ret.extend(ids)

        except Exception as e:
            logger.error('Error: %s, continue', str(e))

    return ret


def doujinshi_parser(id_):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception('Doujinshi id({0}) is not valid'.format(id_))

    id_ = int(id_)
    logger.log(15, 'Fetching doujinshi information of id {0}'.format(id_))
    doujinshi = dict()
    doujinshi['id'] = id_
    url = '{0}/{1}/'.format(constant.DETAIL_URL, id_)

    try:
        response = request('get', url)
        if response.status_code in (200, ):
            response = response.content
        else:
            logger.debug('Slow down and retry ({}) ...'.format(id_))
            time.sleep(1)
            return doujinshi_parser(str(id_))

    except Exception as e:
        logger.critical(str(e))
        raise SystemExit

    html = BeautifulSoup(response, 'html.parser')
    doujinshi_info = html.find('div', attrs={'id': 'info'})

    title = doujinshi_info.find('h1').text
    subtitle = doujinshi_info.find('h2')

    doujinshi['name'] = title
    doujinshi['subtitle'] = subtitle.text if subtitle else ''

    doujinshi_cover = html.find('div', attrs={'id': 'cover'})
    img_id = re.search('/galleries/([\d]+)/cover\.(jpg|png)$', doujinshi_cover.a.img.attrs['data-src'])

    ext = []
    for i in html.find_all('div', attrs={'class': 'thumb-container'}):
        _, ext_name = os.path.basename(i.img.attrs['data-src']).rsplit('.', 1)
        ext.append(ext_name)

    if not img_id:
        logger.critical('Tried yo get image id failed')
        exit(1)

    doujinshi['img_id'] = img_id.group(1)
    doujinshi['ext'] = ext

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
        raise SystemExit

    html = BeautifulSoup(response, 'html.parser')
    doujinshi_search_result = html.find_all('div', attrs={'class': 'gallery'})
    for doujinshi in doujinshi_search_result:
        doujinshi_container = doujinshi.find('div', attrs={'class': 'caption'})
        title = doujinshi_container.text.strip()
        title = title if len(title) < 85 else title[:82] + '...'
        id_ = re.search('/g/(\d+)/', doujinshi.a['href']).group(1)
        result.append({'id': id_, 'title': title})
    if not result:
        logger.warn('Not found anything of keyword {}'.format(keyword))

    return result


def __api_suspended_doujinshi_parser(id_):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception('Doujinshi id({0}) is not valid'.format(id_))

    id_ = int(id_)
    logger.log(15, 'Fetching information of doujinshi id {0}'.format(id_))
    doujinshi = dict()
    doujinshi['id'] = id_
    url = '{0}/{1}'.format(constant.DETAIL_URL, id_)
    i = 0
    while 5 > i:
        try:
            response = request('get', url).json()
        except Exception as e:
            i += 1
            if not i < 5:
                logger.critical(str(e))
                exit(1)
            continue
        break

    doujinshi['name'] = response['title']['english']
    doujinshi['subtitle'] = response['title']['japanese']
    doujinshi['img_id'] = response['media_id']
    doujinshi['ext'] = ''.join(map(lambda s: s['t'], response['images']['pages']))
    doujinshi['pages'] = len(response['images']['pages'])

    # gain information of the doujinshi
    needed_fields = ['character', 'artist', 'language', 'tag']
    for tag in response['tags']:
        tag_type = tag['type']
        if tag_type in needed_fields:
            if tag_type == 'tag':
                if tag_type not in doujinshi:
                    doujinshi[tag_type] = {}

                tag['name'] = tag['name'].replace(' ', '-')
                tag['name'] = tag['name'].lower()
                doujinshi[tag_type][tag['name']] = tag['id']
            elif tag_type not in doujinshi:
                doujinshi[tag_type] = tag['name']
            else:
                doujinshi[tag_type] += ', ' + tag['name']

    return doujinshi


def __api_suspended_search_parser(keyword, page):
    logger.debug('Searching doujinshis using keywords {0}'.format(keyword))
    result = []
    i = 0
    while i < 5:
        try:
            response = request('get', url=constant.SEARCH_URL, params={'query': keyword, 'page': page}).json()
        except Exception as e:
            i += 1
            if not i < 5:
                logger.critical(str(e))
                logger.warn('If you are in China, please configure the proxy to fu*k GFW.')
                exit(1)
            continue
        break

    if 'result' not in response:
        raise Exception('No result in response')

    for row in response['result']:
        title = row['title']['english']
        title = title[:85] + '..' if len(title) > 85 else title
        result.append({'id': row['id'], 'title': title})

    if not result:
        logger.warn('No results for keywords {}'.format(keyword))

    return result


def print_doujinshi(doujinshi_list):
    if not doujinshi_list:
        return
    doujinshi_list = [(i['id'], i['title']) for i in doujinshi_list]
    headers = ['id', 'doujinshi']
    logger.info('Search Result\n' +
                tabulate(tabular_data=doujinshi_list, headers=headers, tablefmt='rst'))


def __api_suspended_tag_parser(tag_id, max_page=1):
    logger.info('Searching for doujinshi with tag id {0}'.format(tag_id))
    result = []
    response = request('get', url=constant.TAG_API_URL, params={'sort': 'popular', 'tag_id': tag_id}).json()
    page = max_page if max_page <= response['num_pages'] else int(response['num_pages'])

    for i in range(1, page + 1):
        logger.info('Getting page {} ...'.format(i))

        if page != 1:
            response = request('get', url=constant.TAG_API_URL,
                               params={'sort': 'popular', 'tag_id': tag_id}).json()
    for row in response['result']:
        title = row['title']['english']
        title = title[:85] + '..' if len(title) > 85 else title
        result.append({'id': row['id'], 'title': title})

    if not result:
        logger.warn('No results for tag id {}'.format(tag_id))

    return result


def tag_parser(tag_name, max_page=1):
    result = []
    tag_name = tag_name.lower()
    tag_name = tag_name.replace(' ', '-')

    for p in range(1, max_page + 1):
        logger.debug('Fetching page {0} for doujinshi with tag \'{1}\''.format(p, tag_name))
        response = request('get', url='%s/%s?page=%d' % (constant.TAG_URL, tag_name, p)).content

        html = BeautifulSoup(response, 'html.parser')
        doujinshi_items = html.find_all('div', attrs={'class': 'gallery'})
        if not doujinshi_items:
            logger.error('Cannot find doujinshi id of tag \'{0}\''.format(tag_name))
            return

        for i in doujinshi_items:
            doujinshi_id = i.a.attrs['href'].strip('/g')
            doujinshi_title = i.a.text.strip()
            doujinshi_title = doujinshi_title if len(doujinshi_title) < 85 else doujinshi_title[:82] + '...'
            result.append({'title': doujinshi_title, 'id': doujinshi_id})

    if not result:
        logger.warn('No results for tag \'{}\''.format(tag_name))

    return result


if __name__ == '__main__':
    print(doujinshi_parser("32271"))
