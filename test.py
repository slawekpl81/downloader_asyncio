import unittest
import requests
from config import path
import main
from filecmp import cmp
import os

class TestMethods(unittest.TestCase):

    def test_correct_download_file(self):
        """test is download file is correct"""
        url = path
        filename = main.get_filename(url)
        copy_file = f'./downloads/{"copy_" + filename}'
        filename = f'./downloads/{filename}'
        r = requests.get(url, allow_redirects=True)
        with open(copy_file, 'wb') as file:
            file.write(r.content)

        os.system('python main.py')

        self.assertTrue(cmp(filename, copy_file), 'Bad download..')

if __name__ == '__main__':
    unittest.main()