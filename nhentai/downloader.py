# coding: utf-

import multiprocessing
import signal

import sys
import os
import requests
import time
import urllib3.exceptions

from urllib.parse import urlparse
from nhentai import constant
from nhentai.logger import logger
from nhentai.parser import request
from nhentai.utils import Singleton


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
semaphore = multiprocessing.Semaphore(1)


class NHentaiImageNotExistException(Exception):
    pass


def download_callback(result):
    result, data = result
    if result == 0:
        logger.warning('fatal errors occurred, ignored')
    elif result == -1:
        logger.warning(f'url {data} return status code 404')
    elif result == -2:
        logger.warning('Ctrl-C pressed, exiting sub processes ...')
    elif result == -3:
        # workers won't be run, just pass
        pass
    else:
        logger.log(16, f'{data} downloaded successfully')


class Downloader(Singleton):

    def __init__(self, path='', size=5, timeout=30, delay=0):
        self.size = size
        self.path = str(path)
        self.timeout = timeout
        self.delay = delay

    def download(self, url, folder='', filename='', retried=0, proxy=None):
        if self.delay:
            time.sleep(self.delay)
        logger.info(f'Starting to download {url} ...')
        filename = filename if filename else os.path.basename(urlparse(url).path)
        base_filename, extension = os.path.splitext(filename)

        save_file_path = os.path.join(folder, base_filename.zfill(3) + extension)
        try:
            if os.path.exists(save_file_path):
                logger.warning(f'Ignored exists file: {save_file_path}')
                return 1, url

            response = None
            with open(save_file_path, "wb") as f:
                i = 0
                while i < 10:
                    try:
                        response = request('get', url, stream=True, timeout=self.timeout, proxies=proxy)
                        if response.status_code != 200:
                            path = urlparse(url).path
                            for mirror in constant.IMAGE_URL_MIRRORS:
                                print(f'{mirror}{path}')
                                mirror_url = f'{mirror}{path}'
                                response = request('get', mirror_url, stream=True,
                                                   timeout=self.timeout, proxies=proxy)
                                if response.status_code == 200:
                                    break

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
                logger.warning(f'Warning: {e}, retrying({retried}) ...')
                return 0, self.download(url=url, folder=folder, filename=filename,
                                        retried=retried+1, proxy=proxy)
            else:
                return 0, None

        except NHentaiImageNotExistException as e:
            os.remove(save_file_path)
            return -1, url

        except Exception as e:
            import traceback
            traceback.print_stack()
            logger.critical(str(e))
            return 0, None

        except KeyboardInterrupt:
            return -3, None

        return 1, url

    def start_download(self, queue, folder='', regenerate_cbz=False):
        if not isinstance(folder, (str, )):
            folder = str(folder)

        if self.path:
            folder = os.path.join(self.path, folder)

        if os.path.exists(folder + '.cbz'):
            if not regenerate_cbz:
                logger.warning(f'CBZ file "{folder}.cbz" exists, ignored download request')
                return

        logger.info(f'Doujinshi will be saved at "{folder}"')
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except EnvironmentError as e:
                logger.critical(str(e))

        else:
            logger.warning(f'Path "{folder}" already exist.')

        queue = [(self, url, folder, constant.CONFIG['proxy']) for url in queue]

        pool = multiprocessing.Pool(self.size, init_worker)
        [pool.apply_async(download_wrapper, args=item) for item in queue]

        pool.close()
        pool.join()


def download_wrapper(obj, url, folder='', proxy=None):
    if sys.platform == 'darwin' or semaphore.get_value():
        return Downloader.download(obj, url=url, folder=folder, proxy=proxy)
    else:
        return -3, None


def init_worker():
    signal.signal(signal.SIGINT, subprocess_signal)


def subprocess_signal(sig, frame):
    if semaphore.acquire(timeout=1):
        logger.warning('Ctrl-C pressed, exiting sub processes ...')

    raise KeyboardInterrupt
