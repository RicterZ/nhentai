import os
import unittest
import urllib3.exceptions

from nhentai import constant
from nhentai.cmdline import load_config
from nhentai.utils import check_cookie


class TestLogin(unittest.TestCase):
    def setUp(self) -> None:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        load_config()
        constant.CONFIG['cookie'] = os.getenv('NHENTAI_COOKIE')
        constant.CONFIG['useragent'] = os.getenv('NHENTAI_UA')

    def test_cookie(self):
        try:
            check_cookie()
            self.assertTrue(True)
        except Exception as e:
            self.assertIsNone(e)


if __name__ == '__main__':
    unittest.main()
