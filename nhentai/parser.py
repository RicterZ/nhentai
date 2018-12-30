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


def request(method, url, **kwargs):
    if not hasattr(requests, method):
        raise AttributeError('\'requests\' object has no attribute \'{0}\''.format(method))

    return requests.__dict__[method](url, proxies=constant.PROXY, verify=False, **kwargs)


def login_parser(username, password):
    s = requests.Session()
    s.proxies = constant.PROXY
    s.verify = False
    s.headers.update({'Referer': constant.LOGIN_URL})

    s.get(constant.LOGIN_URL)
    content = s.get(constant.LOGIN_URL).content
    html = BeautifulSoup(content, 'html.parser')
    csrf_token_elem = html.find('input', attrs={'name': 'csrfmiddlewaretoken'})

    if not csrf_token_elem:
        raise Exception('Cannot find csrf token to login')
    csrf_token = csrf_token_elem.attrs['value']

    login_dict = {
        'csrfmiddlewaretoken': csrf_token,
        'username_or_email': username,
        'password': password,
    }
    resp = s.post(constant.LOGIN_URL, data=login_dict)
    if 'Invalid username/email or password' in resp.text:
        logger.error('Login failed, please check your username and password')
        exit(1)

    html = BeautifulSoup(s.get(constant.FAV_URL).content, 'html.parser')
    count = html.find('span', attrs={'class': 'count'})
    if not count:
        logger.error("Can't get your number of favorited doujins. Did the login failed?")

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

    def _callback(request, result):
        ret.append(result)

    thread_pool = threadpool.ThreadPool(5)

    for page in range(1, pages+1):
        try:
            logger.info('Getting doujinshi ids of page %d' % page)
            resp = s.get(constant.FAV_URL + '?page=%d' % page).text
            ids = doujinshi_id.findall(resp)
            requests_ = threadpool.makeRequests(doujinshi_parser, ids, _callback)
            [thread_pool.putRequest(req) for req in requests_]
            thread_pool.wait()
        except Exception as e:
            logger.error('Error: %s, continue', str(e))

    return ret


def doujinshi_parser(id_):
    if not isinstance(id_, (int,)) and (isinstance(id_, (str,)) and not id_.isdigit()):
        raise Exception('Doujinshi id({0}) is not valid'.format(id_))

    id_ = int(id_)
    logger.log(15, 'Fetching information of doujinshi id {0}'.format(id_))
    doujinshi = dict()
    doujinshi['id'] = id_
    url = '{0}/{1}'.format(constant.DETAIL_URL, id_)
    i=0
    while i<5:
        try:
            response = request('get', url).json()
        except Exception as e:
            i+=1
            if not i<5:
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


def search_parser(keyword, page):
    logger.debug('Searching doujinshis using keywords {0}'.format(keyword))
    result = []
    i=0
    while i<5:
        try:
            response = request('get', url=constant.SEARCH_URL, params={'query': keyword, 'page': page}).json()
        except Exception as e:
            i+=1
            if not i<5:
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


def tag_parser(tag_id, max_page=1):
    logger.info('Searching for doujinshi with tag id {0}'.format(tag_id))
    result = []
    i=0
    while i<5:
        try:
            response = request('get', url=constant.TAG_API_URL, params={'sort': 'popular', 'tag_id': tag_id}).json()
        except Exception as e:
            i+=1
            if not i<5:
                logger.critical(str(e))
                exit(1)
            continue
        break
    page = max_page if max_page <= response['num_pages'] else int(response['num_pages'])

    for i in range(1, page+1):
        logger.info('Getting page {} ...'.format(i))

        if page != 1:
            i=0
            while i<5:
                try:
                    response = request('get', url=constant.TAG_API_URL, params={'sort': 'popular', 'tag_id': tag_id}).json()
                except Exception as e:
                    i+=1
                    if not i<5:
                        logger.critical(str(e))
                        exit(1)
                    continue
                break
    for row in response['result']:
        title = row['title']['english']
        title = title[:85] + '..' if len(title) > 85 else title
        result.append({'id': row['id'], 'title': title})

    if not result:
        logger.warn('No results for tag id {}'.format(tag_id))
    
    return result


def tag_guessing(tag_name):
    tag_name = tag_name.lower()
    tag_name = tag_name.replace(' ', '-')
    logger.info('Trying to get tag_id of tag \'{0}\''.format(tag_name))
    i=0
    while i<5:
        try:
            response = request('get', url='%s/%s' % (constant.TAG_URL, tag_name)).content
        except Exception as e:
            i+=1
            if not i<5:
                logger.critical(str(e))
                exit(1)
            continue
        break

    html = BeautifulSoup(response, 'html.parser')
    first_item = html.find('div', attrs={'class': 'gallery'})
    if not first_item:
        logger.error('Cannot find doujinshi id of tag \'{0}\''.format(tag_name))
        return

    doujinshi_id = re.findall('(\d+)', first_item.a.attrs['href'])
    if not doujinshi_id:
        logger.error('Cannot find doujinshi id of tag \'{0}\''.format(tag_name))
        return

    ret = doujinshi_parser(doujinshi_id[0])
    if 'tag' in ret and tag_name in ret['tag']:
        tag_id = ret['tag'][tag_name]
        logger.info('Tag id of tag \'{0}\' is {1}'.format(tag_name, tag_id))
    else:
        logger.error('Cannot find doujinshi id of tag \'{0}\''.format(tag_name))
        return

    return tag_id


if __name__ == '__main__':
    print(doujinshi_parser("32271"))
