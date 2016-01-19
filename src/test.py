# coding=utf-8
import os

# print os.path.join(__file__, "ñññ", "hola")
# os.system('"C:\\Program Files (x86)\\Web2board\\web2board.exe"')
import time

from libs.Downloader import Downloader
from libs.LoggingUtils import initLogging

log = initLogging(__name__)


def downloaderCallback(*args):
    """
    :type args: list
    """
    list(args).pop(-1)
    print args


Downloader().download("https://github.com/bq/web2board/archive/master.zip", infoCallback=downloaderCallback)

while True:
    time.sleep(2)
