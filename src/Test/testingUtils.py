import os

from flexmock import flexmock

from libs import utils
from libs.CompilerUploader import CompilerUploader
from libs.PathsManager import PathsManager

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
                                   getPort="PORT")
    CompileUploaderConstructorMock = flexmock(CompilerUploader,
                                              construct=lambda *args: compileUploaderMock)

    return compileUploaderMock, CompileUploaderConstructorMock


def createSenderMock():
    class Sender:
        def __init__(self):
            self.isCompiling = lambda: None
            self.isUploading = lambda x: None
            self.ID = None

    return flexmock(Sender(), ID="testID")


def restorePaths():
    PathsManager.__dict__ = {x: y for x, y in __original_pathManagerDict.items()}
