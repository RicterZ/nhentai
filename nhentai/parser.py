# coding: utf-8
import sys
import os
import re
import time
from bs4 import BeautifulSoup
from tabulate import tabulate

import nhentai.constant as constant
from nhentai.utils import request
from nhentai.logger import logger


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
        logger.info(f'CSRF token is {csrf_token}')

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
        sys.exit(1)

    if 'You\'re loading pages way too quickly.' in resp.text or 'Really, slow down' in resp.text:
        logger.error('Using nhentai --cookie \'YOUR_COOKIE_HERE\' to save your Cookie.')
        sys.exit(2)


def _get_title_and_id(response):
    result = []
    html = BeautifulSoup(response, 'html.parser')
    doujinshi_search_result = html.find_all('div', attrs={'class': 'gallery'})
    for doujinshi in doujinshi_search_result:
        doujinshi_container = doujinshi.find('div', attrs={'class': 'caption'})
        title = doujinshi_container.text.strip()
        title = title if len(title) < 85 else title[:82] + '...'
        id_ = re.search('/g/([0-9]+)/', doujinshi.a['href']).group(1)
        result.append({'id': id_, 'title': title})

    return result


def favorites_parser(page=None):
    result = []
    html = BeautifulSoup(request('get', constant.FAV_URL).content, 'html.parser')
    count = html.find('span', attrs={'class': 'count'})
    if not count:
        logger.error("Can't get your number of favorite doujinshis. Did the login failed?")
        return []

    count = int(count.text.strip('(').strip(')').replace(',', ''))
    if count == 0:
        logger.warning('No favorites found')
        return []
    pages = int(count / 25)

    if page:
        page_range_list = page
    else:
        if pages:
            pages += 1 if count % (25 * pages) else 0
        else:
            pages = 1

        logger.info(f'You have {count} favorites in {pages} pages.')

        if os.getenv('DEBUG'):
            pages = 1

        page_range_list = range(1, pages + 1)

    for page in page_range_list:
        try:
            logger.info(f'Getting doujinshi ids of page {page}')
            resp = request('get', f'{constant.FAV_URL}?page={page}').content

            result.extend(_get_title_and_id(resp))
        except Exception as e:
            logger.error(f'Error: {e}, continue')

    return result


def doujinshi_parser(id_, counter=0):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception(f'Doujinshi id({id_}) is not valid')

    id_ = int(id_)
    logger.info(f'Fetching doujinshi information of id {id_}')
    doujinshi = dict()
    doujinshi['id'] = id_
    url = f'{constant.DETAIL_URL}/{id_}/'

    try:
        response = request('get', url)
        if response.status_code in (200, ):
            response = response.content
        elif response.status_code in (404,):
            logger.error(f'Doujinshi with id {id_} cannot be found')
            return []
        else:
            counter += 1

            if counter == 10:
                logger.critical(f'Failed to fetch doujinshi information of id {id_}')
                return None

            logger.debug(f'Slow down and retry ({id_}) ...')
            time.sleep(1)
            return doujinshi_parser(str(id_), counter)

    except Exception as e:
        logger.warning(f'Error: {e}, ignored')
        return None

    # print(response)
    html = BeautifulSoup(response, 'html.parser')
    doujinshi_info = html.find('div', attrs={'id': 'info'})

    title = doujinshi_info.find('h1').text
    pretty_name = doujinshi_info.find('h1').find('span', attrs={'class': 'pretty'}).text
    subtitle = doujinshi_info.find('h2')

    doujinshi['name'] = title
    doujinshi['pretty_name'] = pretty_name
    doujinshi['subtitle'] = subtitle.text if subtitle else ''

    doujinshi_cover = html.find('div', attrs={'id': 'cover'})
    img_id = re.search('/galleries/([0-9]+)/cover.(jpg|png|gif)$',
                       doujinshi_cover.a.img.attrs['data-src'])

    ext = []
    for i in html.find_all('div', attrs={'class': 'thumb-container'}):
        _, ext_name = os.path.basename(i.img.attrs['data-src']).rsplit('.', 1)
        ext.append(ext_name)

    if not img_id:
        logger.critical('Tried yo get image id failed')
        sys.exit(1)

    doujinshi['img_id'] = img_id.group(1)
    doujinshi['ext'] = ext

    pages = 0
    for _ in doujinshi_info.find_all('div', class_='tag-container field-name'):
        if re.search('Pages:', _.text):
            pages = _.find('span', class_='name').string
    doujinshi['pages'] = int(pages)

    # gain information of the doujinshi
    information_fields = doujinshi_info.find_all('div', attrs={'class': 'field-name'})
    needed_fields = ['Characters', 'Artists', 'Languages', 'Tags', 'Parodies', 'Groups', 'Categories']
    for field in information_fields:
        field_name = field.contents[0].strip().strip(':')
        if field_name in needed_fields:
            data = [sub_field.find('span', attrs={'class': 'name'}).contents[0].strip() for sub_field in
                    field.find_all('a', attrs={'class': 'tag'})]
            doujinshi[field_name.lower()] = ', '.join(data)

    time_field = doujinshi_info.find('time')
    if time_field.has_attr('datetime'):
        doujinshi['date'] = time_field['datetime']
    return doujinshi


def legacy_doujinshi_parser(id_):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception(f'Doujinshi id({id_}) is not valid')

    id_ = int(id_)
    logger.info(f'Fetching information of doujinshi id {id_}')
    doujinshi = dict()
    doujinshi['id'] = id_
    url = f'{constant.DETAIL_URL}/{id_}'
    i = 0
    while 5 > i:
        try:
            response = request('get', url).json()
        except Exception as e:
            i += 1
            if not i < 5:
                logger.critical(str(e))
                sys.exit(1)
            continue
        break

    doujinshi['name'] = response['title']['english']
    doujinshi['subtitle'] = response['title']['japanese']
    doujinshi['img_id'] = response['media_id']
    doujinshi['ext'] = ''.join([i['t'] for i in response['images']['pages']])
    doujinshi['pages'] = len(response['images']['pages'])

    # gain information of the doujinshi
    needed_fields = ['character', 'artist', 'language', 'tag', 'parody', 'group', 'category']
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


def print_doujinshi(doujinshi_list):
    if not doujinshi_list:
        return
    doujinshi_list = [(i['id'], i['title']) for i in doujinshi_list]
    headers = ['id', 'doujinshi']
    logger.info(f'Search Result || Found {doujinshi_list.__len__()} doujinshis')
    print(tabulate(tabular_data=doujinshi_list, headers=headers, tablefmt='rst'))


def legacy_search_parser(keyword, sorting, page, is_page_all=False, type_='SEARCH'):
    logger.info(f'Searching doujinshis of keyword {keyword}')
    result = []

    if type_ not in ('SEARCH', 'ARTIST', ):
        raise ValueError('Invalid type')

    if is_page_all:
        if type_ == 'SEARCH':
            response = request('get', url=constant.LEGACY_SEARCH_URL,
                               params={'q': keyword, 'page': 1, 'sort': sorting}).content
        else:
            url = constant.ARTIST_URL + keyword + '/' + ('' if sorting == 'recent' else sorting)
            response = request('get', url=url, params={'page': 1}).content

        html = BeautifulSoup(response, 'lxml')
        pagination = html.find(attrs={'class': 'pagination'})
        last_page = pagination.find(attrs={'class': 'last'})
        last_page = re.findall('page=([0-9]+)', last_page.attrs['href'])[0]
        logger.info(f'Getting doujinshi ids of {last_page} pages')
        pages = range(1, int(last_page))
    else:
        pages = page

    for p in pages:
        logger.info(f'Fetching page {p} ...')
        if type_ == 'SEARCH':
            response = request('get', url=constant.LEGACY_SEARCH_URL,
                               params={'q': keyword, 'page': p, 'sort': sorting}).content
        else:
            url = constant.ARTIST_URL + keyword + '/' + ('' if sorting == 'recent' else sorting)
            response = request('get', url=url, params={'page': p}).content

        if response is None:
            logger.warning(f'No result in response in page {p}')
            continue
        result.extend(_get_title_and_id(response))

    if not result:
        logger.warning(f'No results for keywords {keyword}')

    return result


def search_parser(keyword, sorting, page, is_page_all=False):
    result = []
    response = None
    if not page:
        page = [1]

    if is_page_all:
        url = request('get', url=constant.SEARCH_URL, params={'query': keyword}).url
        init_response = request('get', url.replace('%2B', '+')).json()
        page = range(1, init_response['num_pages']+1)

    total = f'/{page[-1]}' if is_page_all else ''
    not_exists_persist = False
    for p in page:
        i = 0

        logger.info(f'Searching doujinshis using keywords "{keyword}" on page {p}{total}')
        while i < 3:
            try:
                url = request('get', url=constant.SEARCH_URL, params={'query': keyword,
                                                                      'page': p, 'sort': sorting}).url

                if constant.DEBUG:
                    logger.debug(f'Request URL: {url}')

                response = request('get', url.replace('%2B', '+')).json()
            except Exception as e:
                logger.critical(str(e))
                response = None
            break

        if constant.DEBUG:
            logger.debug(f'Response: {response}')

        if response is None or 'result' not in response:
            logger.warning(f'No result in response in page {p}')
            if not_exists_persist is True:
                break
            continue

        for row in response['result']:
            title = row['title']['english']
            title = title[:constant.CONFIG['max_filename']] + '..' if \
                len(title) > constant.CONFIG['max_filename'] else title

            result.append({'id': row['id'], 'title': title})

        not_exists_persist = False
        if not result:
            logger.warning(f'No results for keywords {keyword}')

    return result


if __name__ == '__main__':
    print(doujinshi_parser("32271"))
