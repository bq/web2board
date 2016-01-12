import os
import time
import unittest

import libs.base
from libs import utils

class TestUtils(unittest.TestCase):

    def test_downloadFile_savesDataInTmpFile(self):
        url = "https://raw.githubusercontent.com/bq/web2board/master/README.md"

        tempFile = utils.downloadFile(url)

        self.assertTrue(os.path.exists(tempFile))
        self.assertIn(libs.base.sys_path.get_tmp_path().lower(), tempFile.lower())