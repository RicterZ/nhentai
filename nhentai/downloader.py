# coding: utf-
from __future__ import unicode_literals, print_function

import multiprocessing
import signal

from future.builtins import str as text
import sys
import os
import requests
import time

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from nhentai.logger import logger
from nhentai.parser import request
from nhentai.utils import Singleton

requests.packages.urllib3.disable_warnings()
semaphore = multiprocessing.Semaphore(1)


class NHentaiImageNotExistException(Exception):
    pass


class Downloader(Singleton):

    def __init__(self, path='', size=5, timeout=30, delay=0):
        self.size = size
        self.path = str(path)
        self.timeout = timeout
        self.delay = delay

    def download_(self, url, folder='', filename='', retried=0):
        if self.delay:
            time.sleep(self.delay)
        logger.info('Starting to download {0} ...'.format(url))
        filename = filename if filename else os.path.basename(urlparse(url).path)
        base_filename, extension = os.path.splitext(filename)
        try:
            if os.path.exists(os.path.join(folder, base_filename.zfill(3) + extension)):
                logger.warning('File: {0} exists, ignoring'.format(os.path.join(folder, base_filename.zfill(3) +
                                                                                extension)))
                return 1, url

            response = None
            with open(os.path.join(folder, base_filename.zfill(3) + extension), "wb") as f:
                i = 0
                while i < 10:
                    try:
                        response = request('get', url, stream=True, timeout=self.timeout)
                        if response.status_code != 200:
                            raise NHentaiImageNotExistException

                    except NHentaiImageNotExistException as e:
                        raise e

                    except Exception as e:
                        i += 1
                        if not i < 10:
                            logger.critical(str(e))
                            return 0, None
                        continue

                    break

                length = response.headers.get('content-length')
                if length is None:
                    f.write(response.content)
                else:
                    for chunk in response.iter_content(2048):
                        f.write(chunk)

        except (requests.HTTPError, requests.Timeout) as e:
            if retried < 3:
                logger.warning('Warning: {0}, retrying({1}) ...'.format(str(e), retried))
                return 0, self.download_(url=url, folder=folder, filename=filename, retried=retried+1)
            else:
                return 0, None

        except NHentaiImageNotExistException as e:
            os.remove(os.path.join(folder, base_filename.zfill(3) + extension))
            return -1, url

        except Exception as e:
            import traceback
            traceback.print_stack()
            logger.critical(str(e))
            return 0, None

        except KeyboardInterrupt:
            return -3, None

        return 1, url

    def _download_callback(self, result):
        result, data = result
        if result == 0:
            logger.warning('fatal errors occurred, ignored')
            # exit(1)
        elif result == -1:
            logger.warning('url {} return status code 404'.format(data))
        elif result == -2:
            logger.warning('Ctrl-C pressed, exiting sub processes ...')
        elif result == -3:
            # workers wont be run, just pass
            pass
        else:
            logger.log(15, '{0} downloaded successfully'.format(data))

    def download(self, queue, folder=''):
        if not isinstance(folder, text):
            folder = str(folder)

        if self.path:
            folder = os.path.join(self.path, folder)

        if not os.path.exists(folder):
            logger.warn('Path \'{0}\' does not exist, creating.'.format(folder))
            try:
                os.makedirs(folder)
            except EnvironmentError as e:
                logger.critical('{0}'.format(str(e)))

        else:
            logger.warn('Path \'{0}\' already exist.'.format(folder))

        queue = [(self, url, folder) for url in queue]

        pool = multiprocessing.Pool(self.size, init_worker)
        [pool.apply_async(download_wrapper, args=item) for item in queue]

        pool.close()
        pool.join()


def download_wrapper(obj, url, folder=''):
    if sys.platform == 'darwin' or semaphore.get_value():
        return Downloader.download_(obj, url=url, folder=folder)
    else:
        return -3, None


def init_worker():
    signal.signal(signal.SIGINT, subprocess_signal)


def subprocess_signal(signal, frame):
    if semaphore.acquire(timeout=1):
        logger.warning('Ctrl-C pressed, exiting sub processes ...')

    raise KeyboardInterrupt
