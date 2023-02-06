import unittest
import os
import urllib3.exceptions

from nhentai import constant
from nhentai.cmdline import load_config
from nhentai.downloader import Downloader
from nhentai.parser import doujinshi_parser
from nhentai.doujinshi import Doujinshi
from nhentai.utils import generate_html, generate_cbz


class TestDownload(unittest.TestCase):
    def setUp(self) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        load_config()
        constant.CONFIG['cookie'] = os.getenv('NHENTAI_COOKIE')
        constant.CONFIG['useragent'] = os.getenv('NHENTAI_UA')

    def test_download(self):
        did = 440546
        info = Doujinshi(**doujinshi_parser(did), name_format='%i')
        info.downloader = Downloader(path='/tmp', size=5)
        info.download()

        self.assertTrue(os.path.exists(f'/tmp/{did}/001.jpg'))

        generate_html('/tmp', info)
        self.assertTrue(os.path.exists(f'/tmp/{did}/index.html'))

        generate_cbz('/tmp', info)
        self.assertTrue(os.path.exists(f'/tmp/{did}.cbz'))


if __name__ == '__main__':
    unittest.main()
