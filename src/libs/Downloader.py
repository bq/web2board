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
    def __realDownload(self, url, dst):
        urllib.urlretrieve(url, dst)

    @asynchronous()
    def download(self, url, dst=None, infoCallback=None, endCallback=None):
        if dst is None:
            dst = url.rsplit("/", 1)[1]

        downloadTask = self.__realDownload(url, dst)
        for i in range(3):
            try:
                site = urllib.urlopen(url)
                meta = site.info()
                totalSize = int(meta.getheaders("Content-Length")[0])
                break
            except:
                self.log.warning("Unable to get download file info. retrying in 0.5s")
                time.sleep(1)
        else:
            self.log.error("Unable to download file")
            totalSize = sys.maxint

        while not downloadTask.done():
            if os.path.exists(dst):
                pathSize = os.path.getsize(dst)
                if infoCallback is not None:
                    infoCallback(pathSize, totalSize, pathSize * 100.0 / float(totalSize))
                time.sleep(self.refreshTime)

        if endCallback is not None:
            downloadTask.add_done_callback(endCallback)
        return downloadTask.result()
