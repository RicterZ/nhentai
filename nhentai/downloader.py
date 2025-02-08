# coding: utf-

import os
import asyncio
import httpx
import urllib3.exceptions

from urllib.parse import urlparse
from nhentai import constant
from nhentai.logger import logger
from nhentai.utils import Singleton, async_request


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    def __init__(self, path='', threads=5, timeout=30, delay=0, retry=3, exit_on_fail=False,
                 no_filename_padding=False):
        self.threads = threads
        self.path = str(path)
        self.timeout = timeout
        self.delay = delay
        self.retry = retry
        self.exit_on_fail = exit_on_fail
        self.folder = None
        self.semaphore = None
        self.no_filename_padding = no_filename_padding

    async def fiber(self, tasks):
        self.semaphore = asyncio.Semaphore(self.threads)
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                if result[0] > 0:
                    logger.info(f'{result[1]} download completed')
                else:
                    raise Exception(f'{result[1]} download failed, return value {result[0]}')
            except Exception as e:
                logger.error(f'An error occurred: {e}')
                if self.exit_on_fail:
                    raise Exception('User intends to exit on fail')

    async def _semaphore_download(self, *args, **kwargs):
        async with self.semaphore:
            return await self.download(*args, **kwargs)

    async def download(self, url, folder='', filename='', retried=0, proxy=None, length=0):
        logger.info(f'Starting to download {url} ...')

        if self.delay:
            await asyncio.sleep(self.delay)

        filename = filename if filename else os.path.basename(urlparse(url).path)
        base_filename, extension = os.path.splitext(filename)

        if not self.no_filename_padding:
            filename = base_filename.zfill(length) + extension
        else:
            filename = base_filename + extension

        save_file_path = os.path.join(self.folder, filename)

        try:
            if os.path.exists(save_file_path):
                logger.warning(f'Skipped download: {save_file_path} already exists')
                return 1, url

            response = await async_request('GET', url, timeout=self.timeout, proxy=proxy)

            if response.status_code != 200:
                path = urlparse(url).path
                for mirror in constant.IMAGE_URL_MIRRORS:
                    logger.info(f"Try mirror: {mirror}{path}")
                    mirror_url = f'{mirror}{path}'
                    response = await async_request('GET', mirror_url, timeout=self.timeout, proxies=proxy)
                    if response.status_code == 200:
                        break

            if not await self.save(filename, response):
                logger.error(f'Can not download image {url}')
                return -1, url

        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError) as e:
            if retried < self.retry:
                logger.warning(f'Download {filename} failed, retrying({retried + 1}) times...')
                return await self.download(
                    url=url,
                    folder=folder,
                    filename=filename,
                    retried=retried + 1,
                    proxy=proxy,
                )
            else:
                logger.warning(f'Download {filename} failed with {self.retry} times retried, skipped')
                return -2, url

        except NHentaiImageNotExistException as e:
            os.remove(save_file_path)
            return -3, url

        except Exception as e:
            import traceback

            logger.error(f"Exception type: {type(e)}")
            traceback.print_stack()
            logger.critical(str(e))
            return -9, url

        except KeyboardInterrupt:
            return -4, url

        return 1, url

    async def save(self, save_file_path, response) -> bool:
        if response is None:
            logger.error('Error: Response is None')
            return False
        save_file_path = os.path.join(self.folder, save_file_path)
        with open(save_file_path, 'wb') as f:
            if response is not None:
                length = response.headers.get('content-length')
                if length is None:
                    f.write(response.content)
                else:
                    async for chunk in response.aiter_bytes(2048):
                        f.write(chunk)
        return True

    def start_download(self, queue, folder='') -> bool:
        if not isinstance(folder, (str,)):
            folder = str(folder)

        if self.path:
            folder = os.path.join(self.path, folder)

        logger.info(f'Doujinshi will be saved at "{folder}"')
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except EnvironmentError as e:
                logger.critical(str(e))
        self.folder = folder

        if os.getenv('DEBUG', None) == 'NODOWNLOAD':
            # Assuming we want to continue with rest of process.
            return True

        digit_length = len(str(len(queue)))
        logger.info(f'Total download pages: {len(queue)}')
        coroutines = [
            self._semaphore_download(url, filename=os.path.basename(urlparse(url).path), length=digit_length)
            for url in queue
        ]

        # Prevent coroutines infection
        asyncio.run(self.fiber(coroutines))

        return True
