import time
import unittest
import urllib
from flexmock import flexmock, flexmock_teardown

from libs.Downloader import Downloader


class TestDownloader(unittest.TestCase):
    def setUp(self):
        global urllib
        self.downloader = Downloader(refreshTime=0.01)

        self.original_urlOpen = urllib.urlopen
        self.original_urlretrieve = urllib.urlretrieve

        self.metaMock = flexmock(getheaders=lambda x: [1000])
        self.siteMock = flexmock(info=lambda: self.metaMock)

        self.urlopenMock = flexmock(urllib).should_receive("urlopen").and_return(self.siteMock)

    def tearDown(self):
        urllib.urlopen = self.original_urlOpen
        urllib.urlretrieve = self.original_urlretrieve

    def __infoCallbackMock(self, *args):
        pass

    def __finishCallbackMock(self, *args):
        pass

    def test_download_callsUrlretrieveWithRightArguments(self):
        url = "url"
        dst = "dst"
        self.urlopenMock.once()
        flexmock(urllib).should_receive("urlretrieve").with_args(url, dst).once()

        self.downloader.download(url, dst).result()

    def test_download_callsInfoCallback(self):
        url = "url"
        dst = __file__

        def __waitingFunction(*args):
            time.sleep(0.05)

        urllib.urlretrieve = __waitingFunction
        self.urlopenMock.once()
        flexmock(self).should_call("__infoCallbackMock") \
            .with_args(object, 1000, float).at_least().times(1)
        flexmock(self.downloader).should_call("__real_download").with_args(url, dst).once()

        self.downloader.download(url, dst, info_callback=self.__infoCallbackMock).result()

    def test_download_callsFinishCallback(self):
        url = "url"
        dst = __file__

        self.urlopenMock.once()
        flexmock(self).should_receive("__finishCallbackMock").at_least().times(1)
        flexmock(urllib).should_receive("urlretrieve").with_args(url, dst).once()

        self.downloader.download(url, dst, end_callback=self.__finishCallbackMock).result()
