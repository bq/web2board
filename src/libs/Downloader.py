import logging
import os
import urllib
import time
import sys
import urllib2

from libs.Decorators.Asynchronous import asynchronous


class Downloader:
    log = logging.getLogger(__name__)

    def __init__(self, refreshTime=0.2):
        self.refreshTime = refreshTime

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

        site = urllib2.urlopen(url)
        download_task = self.__real_download(site, dst)
        for i in range(3):
            try:
                meta = site.info()
                total_size = int(meta.getheaders("Content-Length")[0])
                break
            except:
                self.log.exception("Unable to get download file info. retrying in 1s")
                time.sleep(1)

        else:
            self.log.error("Unable to download file")
            total_size = sys.maxint

        while not download_task.done():
            if os.path.exists(dst):
                pathSize = os.path.getsize(dst)
                if info_callback is not None:
                    info_callback(pathSize, total_size, pathSize * 100.0 / float(total_size))
                time.sleep(self.refreshTime)

        return download_task.result()
