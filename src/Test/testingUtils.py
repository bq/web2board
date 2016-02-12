import os
import shutil
from flexmock import flexmock
from wshubsapi.ConnectedClient import ConnectedClient

from libs.CompilerUploader import CompilerUploader
from libs.PathsManager import PathsManager
from libs import utils
from wshubsapi.CommEnvironment import _DEFAULT_PICKER


__original_pathManagerDict = {x: y for x, y in PathsManager.__dict__.items()}

def restoreAllTestResources():
    if os.path.exists(PathsManager.TEST_SETTINGS_PATH):
        utils.rmtree(PathsManager.TEST_SETTINGS_PATH)
    else:
        os.makedirs(PathsManager.TEST_SETTINGS_PATH)
    utils.copytree(PathsManager.TEST_RES_PATH, PathsManager.TEST_SETTINGS_PATH, ignore=".pioenvs", forceCopy=True)


def createCompilerUploaderMock():
    compileUploaderMock = flexmock(CompilerUploader(),
                                   compile=lambda *args: [True, None],
                                   getPort=None)
    CompileUploaderConstructorMock = flexmock(CompilerUploader,
                                              construct=lambda *args: compileUploaderMock)

    return compileUploaderMock, CompileUploaderConstructorMock


def createSenderMock():
    class Sender:
        def __init__(self):
            self.isCompiling = lambda: None
            self.isUploading = lambda x: None

        def __getitem__(self, item):
            return ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x)

    return flexmock(Sender())


def restorePaths():
    PathsManager.__dict__ = {x: y for x, y in __original_pathManagerDict.items()}
