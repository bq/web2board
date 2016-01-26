import logging
import os
import urllib

import time

from libs.Decorators.Asynchronous import asynchronous

class Downloader:
    log = logging.getLogger(__name__)

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
        for i in range(3):
            try:
                site = urllib.urlopen(url)
                meta = site.info()
                totalSize = meta.getheaders("Content-Length")[0]
                break
            except:
                self.log.error("Unable to get download file info. retraing in 0.5s")
                time.sleep(0.5)
        else:
            raise Exception("Unable to download new version")

        while not downloadTask.isDone():
            if os.path.exists(dst):
                pathSize = os.path.getsize(dst)
                if infoCallback is not None:
                    infoCallback(pathSize, totalSize, pathSize * 100.0 / float(totalSize))
                time.sleep(self.refreshTime)

        if finishCallback is not None:
            finishCallback(downloadTask.get())
        return downloadTask.get()
