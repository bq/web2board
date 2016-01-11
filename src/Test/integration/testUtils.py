import os
import time
import unittest

import libs.base
from libs import utils

class TestUtils(unittest.TestCase):

    def test_downloadFile_savesDataInTmpFile(self):
        url = "https://raw.githubusercontent.com/bq/web2board/master/README.md"

        tempFile = utils.downloadFile(url)

        lastModificationFile = os.stat(tempFile).st_mtime
        lastModificationDiff = time.time() - lastModificationFile
        self.assertTrue(abs(lastModificationDiff) < 0.5)
        self.assertIn(libs.base.sys_path.get_tmp_path().lower(), tempFile.lower())