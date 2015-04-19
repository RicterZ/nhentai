#coding: utf-8
import os
import sys
import threading
import Queue
import requests
from urlparse import urlparse
from hentai.logger import logger

shutdown = threading.Event()

class Downloader(object):
    def __init__(self, path='', thread=1):
        if not isinstance(thread, (int, )) or thread < 1 or thread > 10:
            raise ValueError('Invalid threads count')
        self.path = str(path)
        self.thread_count = thread
        self.threads = []

    def _download(self, url, folder='', filename=''):
        if shutdown.is_set():
            return

        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except os.error, e:
                logger.error('Error %s' % str(e))
                sys.exit()

        filename = filename if filename else os.path.basename(urlparse(url).path)
        try:
            with open(os.path.join(folder, filename), "wb") as f:
                response = requests.get(url, stream=True)
                length = response.headers.get('content-length')
                if length is None:
                    f.write(response.content)
                else:
                    for chunk in response.iter_content(2048):
                        f.write(chunk)
        except (os.error, IOError), e:
            logger.error('Error %s' % e)
            sys.exit()

        except Exception, e:
            raise e

        logger.info('%s downloaded: %s done!' % (threading.currentThread().getName(), url))

    def _download_thread(self, queue, folder=''):
        while True:
            if queue.empty():
                queue.task_done()
                break
            try:
                url = queue.get(False)
                logger.info('%s downloading: %s ...' % (threading.currentThread().getName(), url))
                self._download(url, folder)
            except Queue.Empty:
                break

    def download(self, queue, folder=''):
        if not isinstance(folder, (str, unicode)):
            folder = str(folder)

        if self.path:
            folder = self.path

        if os.path.exists(path=folder):
            logger.warn('Path \'%s\' already exist' % folder)
        else:
            logger.warn('Path \'%s\' not exist' % folder)

        for i in range(self.thread_count):
            _ = threading.Thread(target=self._download_thread, args=(queue, folder, ))
            _.setDaemon(True)
            self.threads.append(_)

        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()

        logger.log(15, u'🍺 All done, saved to \'%s\'!' % folder)

