#coding: utf-8
import os
import requests
import threadpool
from urlparse import urlparse
from logger import logger


class Downloader(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Downloader, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, path='', thread=1, timeout=30):
        if not isinstance(thread, (int, )) or thread < 1 or thread > 10:
            raise ValueError('Invalid threads count')
        self.path = str(path)
        self.thread_count = thread
        self.threads = []
        self.timeout = timeout

    def _download(self, url, folder='', filename='', retried=False):
        logger.info('Start downloading: %s ...' % url)
        filename = filename if filename else os.path.basename(urlparse(url).path)
        try:
            with open(os.path.join(folder, filename), "wb") as f:
                response = requests.get(url, stream=True, timeout=self.timeout)
                length = response.headers.get('content-length')
                if length is None:
                    f.write(response.content)
                else:
                    for chunk in response.iter_content(2048):
                        f.write(chunk)
        except (os.error, IOError), e:
            if not retried:
                logger.error('Error: %s, retrying' % str(e))
                return self._download(url=url, folder=folder, filename=filename, retried=True)
            else:
                return None
        except Exception, e:
            logger.critical('CRITICAL: %s' % str(e))
            raise e
        return url

    def _download_callback(self, request, result):
        if not result:
            logger.critical('Too many network errors occurred, please check your connection.')
            raise SystemExit
        logger.log(15, '%s download successfully' % result)

    def download(self, queue, folder=''):
        if not isinstance(folder, (str, unicode)):
            folder = str(folder)

        if self.path:
            folder = os.path.join(self.path, folder)

        if not os.path.exists(folder):
            logger.warn('Path \'%s\' not exist.' % folder)
            try:
                os.mkdir(folder)
            except os.error, e:
                logger.critical('Error: %s' % str(e))
                raise SystemExit
        else:
            logger.warn('Path \'%s\' already exist.' % folder)

        queue = [([url], {'folder': folder}) for url in queue]

        self.thread_pool = threadpool.ThreadPool(self.thread_count)
        requests_ = threadpool.makeRequests(self._download, queue, self._download_callback)
        [self.thread_pool.putRequest(req) for req in requests_]

        self.thread_pool.wait()
