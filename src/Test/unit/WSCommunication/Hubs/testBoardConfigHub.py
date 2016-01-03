import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.Hub import UnsuccessfulReplay
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses
from wshubsapi.CommEnvironment import _DEFAULT_PICKER
from libs.CompilerUploader import CompilerUploader, CompilerException, ERROR_NO_PORT_FOUND
from libs.LibraryUpdater import getLibUpdater
from libs.WSCommunication.Hubs.BoardConfigHub import BoardConfigHub, BoardConfigHubException

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock


class TestBoardConfigHub(unittest.TestCase):
    def setUp(self):
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.boardConfigHub = HubsInspector.getHubInstance(BoardConfigHub)
        client = ConnectedClient(_DEFAULT_PICKER, None, lambda x=0: x, lambda x=0: x)
        self.sender = flexmock(isSettingPort=lambda x: x, isSettingBoard=lambda: None)
        self.boardConfigHub.compilerUploader = flexmock(self.boardConfigHub.compilerUploader,
                                                        compile=None,
                                                        getPort=None)

        self.testLibVersion = "1.1.1"

        self.libUpdater = getLibUpdater()
        self.libUpdater = flexmock(self.libUpdater,
                                   getBitbloqLibsVersion=self.testLibVersion,
                                   setBitbloqLibsVersion=lambda x: x,
                                   downloadLibsIfNecessary=lambda: 1)

    def tearDown(self):
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
            raise CompilerException(ERROR_NO_PORT_FOUND)

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
        self.libUpdater.should_receive("downloadLibsIfNecessary").never()

        self.boardConfigHub.setLibVersion(self.testLibVersion)

    def test_setLibVersion_doesDownloadLibsIfDoesNotHasRightVersion(self):
        self.libUpdater.should_receive("downloadLibsIfNecessary").once()

        self.boardConfigHub.setLibVersion(self.testLibVersion + "new")

    def test_setLibVersion_returnsTrue(self):
        self.assertTrue(self.boardConfigHub.setLibVersion(self.testLibVersion))
        self.assertTrue(self.boardConfigHub.setLibVersion(self.testLibVersion + "new"))
