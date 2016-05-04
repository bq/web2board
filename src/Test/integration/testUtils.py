import os
import unittest
import tempfile
from libs import utils


class TestUtils(unittest.TestCase):

    def test_downloadFile_savesDataInTmpFile(self):
        url = "https://raw.githubusercontent.com/bq/web2board/master/README.md"

        temporaryFile = utils.downloadFile(url)

        self.assertTrue(os.path.exists(temporaryFile))
        self.assertIn(tempfile.gettempdir(), temporaryFile.lower())