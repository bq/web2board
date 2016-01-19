import os
import urllib

import time

from libs.Decorators.Asynchronous import asynchronous


class Downloader:
    def __init__(self, refreshTime=0.2):
        self.refreshTime = refreshTime

    @asynchronous()
    def __realDownload(self, url, dst):
        urllib.urlretrieve(url, dst)

    @asynchronous()
    def download(self, url, dst=None, infoCallback=None, finishCallback=None):
        if dst is None:
            dst = url.rsplit("/", 1)[1]

        downloadTask = self.__realDownload(url, dst)
        site = urllib.urlopen(url)
        meta = site.info()
        totalSize = meta.getheaders("Content-Length")[0]

        while not downloadTask.isDone():
            if os.path.exists(dst):
                pathSize = os.path.getsize("master.zip")
                if infoCallback is not None:
                    infoCallback(pathSize, totalSize, pathSize * 100.0 / float(totalSize))
                time.sleep(self.refreshTime)

        if finishCallback is not None:
            finishCallback(downloadTask.get())
