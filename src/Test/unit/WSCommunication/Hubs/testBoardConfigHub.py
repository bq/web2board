import unittest

import sys
from PySide.QtGui import QApplication
from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER

from Test.testingUtils import restoreAllTestResources
from frames.Web2boardWindow import Web2boardWindow
from libs.CompilerUploader import CompilerUploader, CompilerException, ERROR_NO_PORT_FOUND
from libs.Decorators.InGuiThread import Result
from libs.MainApp import getMainApp
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
from libs.WSCommunication.Hubs.BoardConfigHub import BoardConfigHub, BoardConfigHubException

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock

try:
    QApplication(sys.argv)
except:
    pass

class TestBoardConfigHub(unittest.TestCase):

    def setUp(self):
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.libUpdater = getBitbloqLibsUpdater()
        self.updater = getWeb2boardUpdater()
        self.boardConfigHub = HubsInspector.getHubInstance(BoardConfigHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x)
        self.sender = flexmock(isSettingPort=lambda x: x, isSettingBoard=lambda: None)

        self.original_compile = self.boardConfigHub.compilerUploader.compile
        self.original_getPort = self.boardConfigHub.compilerUploader.getPort
        self.original_lib_update = self.libUpdater.update

        self.original_updater_downloadVersion = self.updater.downloadVersion
        self.original_updater_makeAnAuxiliaryCopy = self.updater.makeAnAuxiliaryCopy
        self.original_updater_runAuxiliaryCopy = self.updater.runAuxiliaryCopy

        self.boardConfigHub.compilerUploader = flexmock(self.boardConfigHub.compilerUploader,
                                                        compile=None,
                                                        getPort=None)
        self.testLibVersion = "1.1.1"

        restoreAllTestResources()

    def tearDown(self):
        self.boardConfigHub.compilerUploader.compile = self.original_compile
        self.boardConfigHub.compilerUploader.getPort = self.original_compile
        self.libUpdater.update = self.original_lib_update

        self.updater.downloadVersion = self.original_updater_downloadVersion
        self.updater.makeAnAuxiliaryCopy = self.original_updater_makeAnAuxiliaryCopy
        self.updater.runAuxiliaryCopy = self.original_updater_runAuxiliaryCopy

        removeHubsSubclasses()

    def test_construct_getCompilerUploader(self):
        self.assertIsInstance(self.boardConfigHub.compilerUploader, CompilerUploader)

    def test_getVersion_returnsAVersionStringFormat(self):
        version = self.boardConfigHub.getVersion()

        self.assertRegexpMatches(version, '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')

    def test_setBoard_raisesExceptionIfBoardIsUndefined(self):
        self.sender.should_receive("isSettingBoard").never()
        self.sender.should_receive("isSettingPort").never()

        with self.assertRaises(BoardConfigHubException) as cm:
            self.boardConfigHub.setBoard("undefined", self.sender)

        self.assertEqual(str(cm.exception), 'BOARD UNDEFINED')

    def test_setBoard_raisesExceptionIfBoardIsNotSupported(self):
        self.sender.should_receive("isSettingBoard").once()
        self.sender.should_receive("isSettingPort").never()

        with self.assertRaises(BoardConfigHubException) as cm:
            self.boardConfigHub.setBoard("12343425234", self.sender)
            self.assertEqual(str(cm.exception), 'NOT SUPPORTED BOARD')

    def test_setBoard_raisesExceptionIfNoPortFound(self):
        self.sender.should_receive("isSettingBoard").once()
        self.sender.should_receive("isSettingPort").never()

        def newGetPort():
            raise CompilerException(ERROR_NO_PORT_FOUND, self.boardConfigHub.compilerUploader.board)

        self.boardConfigHub.compilerUploader.getPort = newGetPort
        with self.assertRaises(BoardConfigHubException) as cm:
            self.boardConfigHub.setBoard("uno", self.sender)
            self.assertEqual(str(cm.exception), 'NO PORT FOUND')

    def test_setBoard_noticeTheClientWhenSettingBoardAndSettingPort(self):
        self.sender.should_receive("isSettingBoard").once()
        self.sender.should_receive("isSettingPort").once()

        self.boardConfigHub.setBoard("uno", self.sender)

    def test_setBoard_ReturnsTrueIfSuccessfullyFinished(self):
        self.assertTrue(self.boardConfigHub.setBoard("uno", self.sender))

    def test_setLibVersion_doesNotDownloadLibsIfHasRightVersion(self):
        flexmock(self.libUpdater, isNecessaryToUpdate=lambda **kwargs: False).should_receive("update").never()
        self.libUpdater.currentVersionInfo.version = self.testLibVersion

        self.boardConfigHub.setLibVersion(self.testLibVersion)

    def test_setLibVersion_doesDownloadLibsIfDoesNotHasRightVersion(self):
        self.libUpdater = flexmock(self.libUpdater).should_receive("update").once()

        self.boardConfigHub.setLibVersion(self.testLibVersion)

    def test_setLibVersion_returnsTrue(self):
        self.libUpdater = flexmock(self.libUpdater, update=lambda x: None)
        self.assertTrue(self.boardConfigHub.setLibVersion(self.testLibVersion))
        self.assertTrue(self.boardConfigHub.setLibVersion(self.testLibVersion))

    def test_setWeb2boardVersion_returnsTrue(self):
        resultObject = Result()
        resultObject.actionDone()
        flexmock(self.updater).should_receive("downloadVersion").and_return(resultObject).once()
        flexmock(self.updater).should_receive("makeAnAuxiliaryCopy").once()
        flexmock(self.updater).should_receive("runAuxiliaryCopy").once()
        getMainApp().w2bGui = flexmock(Web2boardWindow())

        self.boardConfigHub.setWeb2boardVersion("0.0.1")
