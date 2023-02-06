import unittest
import os
import urllib3.exceptions

from nhentai import constant
from nhentai.cmdline import load_config
from nhentai.parser import search_parser, doujinshi_parser, favorites_parser


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        load_config()
        constant.CONFIG['cookie'] = os.getenv('NHENTAI_COOKIE')
        constant.CONFIG['useragent'] = os.getenv('NHENTAI_UA')

    def test_search(self):
        result = search_parser('umaru', 'recent', [1], False)
        self.assertTrue(len(result) > 0)

    def test_doujinshi_parser(self):
        result = doujinshi_parser(123456)
        self.assertTrue(result['pages'] == 84)

    def test_favorites_parser(self):
        result = favorites_parser(page=[1])
        self.assertTrue(len(result) > 0)
