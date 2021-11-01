import unittest
import requests
from config import path
import main
from filecmp import cmp
import os
import app_methods


class TestMethods(unittest.TestCase):

    def test_set_parts_500k(self):
        foo500k = app_methods.set_parts(499_000)
        self.assertEqual(foo500k, [[0, 499_000], ])

    def test_set_parts_700k(self):
        foo700k = app_methods.set_parts(650_000)
        self.assertEqual(foo700k, [[0, 325_000], [325_001, 650_000]])

    def test_set_parts_12M(self):
        foo12M = app_methods.set_parts(1_125_000)
        foo_return = [[0, 400_000], [400_001, 800_000], [800_001, 1_125_000]]
        self.assertEqual(foo12M, foo_return)

    # def test_correct_download_file(self):
    #     """test is download file is correct"""
    #     url = path
    #     filename = main.get_filename(url)
    #     copy_file = f'./downloads/{"copy_" + filename}'
    #     filename = f'./downloads/{filename}'
    #     r = requests.get(url, allow_redirects=True)
    #     with open(copy_file, 'wb') as file:
    #         file.write(r.content)
    #
    #     os.system('python main.py')
    #
    #     self.assertTrue(cmp(filename, copy_file), 'Bad download..')


if __name__ == '__main__':
    unittest.main()
