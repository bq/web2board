import logging
import os
import time
import sys
import urllib2

from libs.Decorators.Asynchronous import asynchronous
import warnings

# ignore insecure warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib2')


class Downloader:
    log = logging.getLogger(__name__)

    def __init__(self, refresh_time=0.2):
        self.refreshTime = refresh_time

    @asynchronous()
    def __real_download(self, url_file, dst):
        if os.path.exists(dst):
            os.remove(dst)
        while True:
            read = url_file.read(10000)  # checking every 10 kb
            if not read:
                break
            with open(dst, 'ab') as f:
                f.write(read)

    @asynchronous()
    def download(self, url, dst=None, info_callback=None):
        if dst is None:
            dst = url.rsplit("/", 1)[1]
        if not isinstance(url, str):
            url = str(url)
        self.log("downloading form: %s", url)
        site = urllib2.urlopen(url)
        download_task = self.__real_download(site, dst)
        for i in range(3):
            try:
                meta = urllib2.urlopen(url).info()
                total_size = int(meta.getheaders("Content-Length")[0])
                break
            except:
                self.log.exception("Unable to get download file info. retrying in 1s")
                time.sleep(1)

        else:
            self.log.warning("Unable get download file size")
            total_size = sys.maxint

        while not download_task.done():
            if os.path.exists(dst):
                file_size = os.path.getsize(dst)
                if info_callback is not None:
                    info_callback(file_size, total_size, file_size * 100.0 / float(total_size))
                time.sleep(self.refreshTime)

        return download_task.result()
