import logging
import os
import urllib

import time

import sys

from libs.Decorators.Asynchronous import asynchronous


class Downloader:
    log = logging.getLogger(__name__)

    def __init__(self, refreshTime=0.2):
        self.refreshTime = refreshTime

    @asynchronous()
    def __real_download(self, url, dst):
        urllib.urlretrieve(url, dst)

    @asynchronous()
    def download(self, url, dst=None, info_callback=None, end_callback=None):
        if dst is None:
            dst = url.rsplit("/", 1)[1]

        download_task = self.__real_download(url, dst)
        for i in range(3):
            try:
                site = urllib.urlopen(url)
                meta = site.info()
                total_size = int(meta.getheaders("Content-Length")[0])
                break
            except:
                self.log.warning("Unable to get download file info. retrying in 0.5s")
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

        if end_callback is not None:
            download_task.add_done_callback(end_callback)
        return download_task.result()
