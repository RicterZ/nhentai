import unittest
import os
import zipfile
import urllib3.exceptions

from nhentai import constant
from nhentai.cmdline import load_config
from nhentai.downloader import Downloader, CompressedDownloader
from nhentai.parser import doujinshi_parser
from nhentai.doujinshi import Doujinshi
from nhentai.utils import generate_html

did = 440546

def has_jepg_file(path):
    with zipfile.ZipFile(path, 'r') as zf:
        return '01.jpg' in zf.namelist()

def is_zip_file(path):
    try:
        with zipfile.ZipFile(path, 'r') as _:
            return True
    except (zipfile.BadZipFile, FileNotFoundError):
        return False

class TestDownload(unittest.TestCase):
    def setUp(self) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        load_config()
        constant.CONFIG['cookie'] = os.getenv('NHENTAI_COOKIE')
        constant.CONFIG['useragent'] = os.getenv('NHENTAI_UA')

        self.info = Doujinshi(**doujinshi_parser(did), name_format='%i')

    def test_download(self):
        info = self.info
        info.downloader = Downloader(path='/tmp', threads=5)
        info.download()

        self.assertTrue(os.path.exists(f'/tmp/{did}/01.jpg'))

        generate_html('/tmp', info)
        self.assertTrue(os.path.exists(f'/tmp/{did}/index.html'))

    def test_zipfile_download(self):
        info = self.info
        info.downloader = CompressedDownloader(path='/tmp', threads=5)
        info.download()

        zipfile_path = f'/tmp/{did}.zip'
        self.assertTrue(os.path.exists(zipfile_path))
        self.assertTrue(is_zip_file(zipfile_path))
        self.assertTrue(has_jepg_file(zipfile_path))

if __name__ == '__main__':
    unittest.main()
