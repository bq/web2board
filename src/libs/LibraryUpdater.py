#!/usr/bin/python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------#
#                                                                       #
# This file is part of the web2board project                            #
#                                                                       #
# Copyright (C) 2015 Mundo Reader S.L.                                  #
#                                                                       #
# Date: November 2015                                                   #
# Author: Irene Sanz Nieto <irene.sanz@bq.com>                          #
#                                                                       #
# -----------------------------------------------------------------------#
import distutils
import json
import shutil
import zipfile
from distutils.dir_util import mkpath
from urllib2 import urlopen, URLError, HTTPError
from libs.PathConstants import *

__globalLibUpdater = None

##
# Class LibraryUpdater, created to check for downloaded libraries and update them if necessary
#
class LibraryUpdater:
    BITBLOQ_LIBS_URL_TEMPLATE = 'https://github.com/bq/bitbloqLibs/archive/v{}.zip'

    def __init__(self):
        pass

    def updateWeb2BoardVersion(self):
        # Get bitbloqLibs version from config file

        self.__copyConfigInHomeIfNotExists()

        with open(RES_CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            versionTrue = str(data.get('bitbloqLibsVersion', "0.0.0"))

        with open(WEB2BOARD_CONFIG_PATH, "r+") as json_data_file:
            data = json.load(json_data_file)
            versionLocal = str(data['bitbloqLibsVersion'])
            if versionLocal != versionTrue:
                data['bitbloqLibsVersion'] = versionTrue

    def getBitbloqLibsVersion(self):
        # Get bitbloqLibs version from config file
        self.__copyConfigInHomeIfNotExists()
        with open(WEB2BOARD_CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            version = str(data['bitbloqLibsVersion'])
        return version

    def getBitbloqLibsName(self):
        # Get bitbloqLibs name from config file
        self.__copyConfigInHomeIfNotExists()
        with open(WEB2BOARD_CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            bitbloqLibsName = []
            try:
                bitbloqLibsName = data['bitbloqLibsName']
            except:
                print 'No bitbloqLibsName'
                pass
        return bitbloqLibsName

    def setBitbloqLibsVersion(self, newVersion):
        self.__copyConfigInHomeIfNotExists()
        jsonFile = open(WEB2BOARD_CONFIG_PATH, "r")
        data = json.load(jsonFile)
        jsonFile.close()

        data["bitbloqLibsVersion"] = newVersion

        jsonFile = open(WEB2BOARD_CONFIG_PATH, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()

    def setBitbloqLibsNames(self, bitbloqLibsNames):
        self.__copyConfigInHomeIfNotExists()
        if not hasattr(bitbloqLibsNames, "__iter__"):
            raise Exception("bitbloqLibsNames have to be a list, received: {}".format(bitbloqLibsNames))

        with open(WEB2BOARD_CONFIG_PATH, "r") as jsonFile:
            data = json.load(jsonFile)

        data["bitbloqLibsName"] = bitbloqLibsNames

        with open(WEB2BOARD_CONFIG_PATH, "w+") as jsonFile:
            jsonFile.write(json.dumps(data))

        log.info("config ready")

    def downloadFile(self, url, path='.'):
        # Open the url
        try:
            f = urlopen(url)
            log.info("downloading " + url)
            tempFilePath = Web2BoardPaths.getDownloadedFilePath(url)
            # Open our local file for writing
            with open(tempFilePath, "wb") as local_file:
                local_file.write(f.read())

            return tempFilePath
        except HTTPError, e:
            print "HTTP Error:", e.code, url
        except URLError, e:
            print "URL Error:", e.reason, url

    def downloadLibs(self):
        version = self.getBitbloqLibsVersion()
        log.info('Downloading new libs, version: {}'.format(version))

        downloadedFilePath = self.downloadFile(self.BITBLOQ_LIBS_URL_TEMPLATE.format(version))

        self._extractZip(downloadedFilePath, base.sys_path.get_tmp_path())
        log.info('extracting zip')
        self._copyLibsInTmpToBoardsLibsPath(version)
        log.info('copying libraries in Arduino\'s libraries directory')
        self.setBitbloqLibsNames(self._getBitbloqLibsNamesFromDownloadedZip(version))

        # Remove .zip
        try:
            os.remove(downloadedFilePath)
        except OSError as e:
            logging.error('exception: {} raised removing libraries zip file'.format(e))

        logging.info("Bitbloq libs downloaded")

    def areWeMissingLibs(self):
        self.updateWeb2BoardVersion()

        libsNames = self.getBitbloqLibsName()
        if not os.path.exists(SKETCHBOOK_PATH):
            os.makedirs(SKETCHBOOK_PATH)
        if len(libsNames) < 1:
            return True
        else:
            for lib in libsNames:
                libPath = SKETCHBOOK_LIBRARIES_PATH + lib
                if not os.path.exists(libPath) or not os.listdir(libPath):
                    return True
        return False

    def downloadLibsIfNecessary(self):
        if self.areWeMissingLibs():
            self.downloadLibs()

    def _listDirectoriesInPath(self, path):
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

    def _extractZip(self, origin, destination):
        with zipfile.ZipFile(origin, "r") as z:
            z.extractall(destination)

    def _copyLibsInTmpToBoardsLibsPath(self, version):
        tmpPath = Web2BoardPaths.getBitbloqLibsTempPath(version)
        versionNumber = int(version.replace('.', ''))
        if versionNumber <= 2:
            distutils.dir_util.copy_tree(tmpPath, SKETCHBOOK_LIBRARIES_PATH)
        elif versionNumber > 2:
            for name in os.listdir(tmpPath):
                if os.path.isdir(tmpPath + '/' + name):
                    try:
                        distutils.dir_util.copy_tree(tmpPath, SKETCHBOOK_LIBRARIES_PATH)
                    except OSError as e:
                        # todo could we handle this error in main??
                        logging.debug('Error: exception in copy_tree with ' + name)
                        logging.debug(e)
        else:
            raise RuntimeError("version not supported")

    def _getBitbloqLibsNamesFromDownloadedZip(self, version):
        tmpPath = Web2BoardPaths.getBitbloqLibsTempPath(version)
        versionNumber = int(version.replace('.', ''))
        if versionNumber <= 2:
            return ['bitbloqLibs']
        elif versionNumber > 2:
            return self._listDirectoriesInPath(tmpPath)
        else:
            raise RuntimeError("version not supported")

    def __copyConfigInHomeIfNotExists(self):
        if not os.path.isfile(WEB2BOARD_CONFIG_PATH):
            shutil.copyfile(RES_CONFIG_PATH, WEB2BOARD_CONFIG_PATH)


def getLibUpdater():
    """
    :rtype: CompilerUploader
    """
    global __globalLibUpdater
    if __globalLibUpdater is None:
        __globalLibUpdater = LibraryUpdater()
    return __globalLibUpdater
