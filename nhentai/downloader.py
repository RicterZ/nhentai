# coding: utf-
from __future__ import unicode_literals, print_function
from future.builtins import str as text
import os
import requests
import threadpool
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from nhentai.logger import logger
from nhentai.parser import request
from nhentai.utils import Singleton


requests.packages.urllib3.disable_warnings()


class NhentaiImageNotExistException(Exception):
    pass


class Downloader(Singleton):

    def __init__(self, path='', thread=1, timeout=30):
        if not isinstance(thread, (int, )) or thread < 1 or thread > 15:
            raise ValueError('Invalid threads count')
        self.path = str(path)
        self.thread_count = thread
        self.threads = []
        self.timeout = timeout

    def _download(self, url, folder='', filename='', retried=0):
        logger.info('Start downloading: {0} ...'.format(url))
        filename = filename if filename else os.path.basename(urlparse(url).path)
        base_filename, extension = os.path.splitext(filename)
        try:
            with open(os.path.join(folder, base_filename.zfill(3) + extension), "wb") as f:
                response = request('get', url, stream=True, timeout=self.timeout)
                if response.status_code != 200:
                    raise NhentaiImageNotExistException
                length = response.headers.get('content-length')
                if length is None:
                    f.write(response.content)
                else:
                    for chunk in response.iter_content(2048):
                        f.write(chunk)

        except (requests.HTTPError, requests.Timeout) as e:
            if retried < 3:
                logger.warning('Warning: {0}, retrying({1}) ...'.format(str(e), retried))
                return 0, self._download(url=url, folder=folder, filename=filename, retried=retried+1)
            else:
                return 0, None

        except NhentaiImageNotExistException as e:
            os.remove(os.path.join(folder, base_filename.zfill(3) + extension))
            return -1, url

        except Exception as e:
            logger.critical(str(e))
            return 0, None

        return 1, url

    def _download_callback(self, request, result):
        result, data = result
        if result == 0:
            logger.critical('fatal errors occurred, quit.')
            exit(1)
        elif result == -1:
            logger.warning('url {} return status code 404'.format(data))
        else:
            logger.log(15, '{0} download successfully'.format(data))

    def download(self, queue, folder=''):
        if not isinstance(folder, (text)):
            folder = str(folder)

        if self.path:
            folder = os.path.join(self.path, folder)

        if not os.path.exists(folder):
            logger.warn('Path \'{0}\' not exist.'.format(folder))
            try:
                os.makedirs(folder)
            except EnvironmentError as e:
                logger.critical('{0}'.format(str(e)))
                exit(1)
        else:
            logger.warn('Path \'{0}\' already exist.'.format(folder))

        queue = [([url], {'folder': folder}) for url in queue]

        self.thread_pool = threadpool.ThreadPool(self.thread_count)
        requests_ = threadpool.makeRequests(self._download, queue, self._download_callback)
        [self.thread_pool.putRequest(req) for req in requests_]

        self.thread_pool.wait()
