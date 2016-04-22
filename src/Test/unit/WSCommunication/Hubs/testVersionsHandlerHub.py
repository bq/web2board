import unittest

import sys
from PySide.QtGui import QApplication
from wshubsapi.hubs_inspector import HubsInspector
from wshubsapi.test.utils.hubs_utils import remove_hubs_subclasses

from Test.testingUtils import restoreAllTestResources, createCompilerUploaderMock, createSenderMock
from libs.Decorators.InGuiThread import Result
from libs.MainApp import getMainApp
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Updaters.Web2boardUpdater import getWeb2boardUpdater
from libs.WSCommunication.Hubs.VersionsHandlerHub import VersionsHandlerHub

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock, flexmock_teardown

try:
    QApplication(sys.argv)
except:
    pass

class TestVersionsHandlerHub(unittest.TestCase):

    def setUp(self):
        HubsInspector.inspect_implemented_hubs(force_reconstruction=True)
        self.libUpdater = getBitbloqLibsUpdater()
        self.updater = getWeb2boardUpdater()
        self.versionsHandlerHub = HubsInspector.get_hub_instance(VersionsHandlerHub)
        """ :type : VersionsHandlerHub"""
        self.sender = createSenderMock()

        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()
        self.testLibVersion = "1.1.1"

        restoreAllTestResources()

    def tearDown(self):
        flexmock_teardown()
        remove_hubs_subclasses()

    def test_getVersion_returnsAVersionStringFormat(self):
        version = self.versionsHandlerHub.getVersion()

        self.assertRegexpMatches(version, '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')

    def test_setLibVersion_doesNotDownloadLibsIfHasRightVersion(self):
        flexmock(self.libUpdater, isNecessaryToUpdate=lambda **kwargs: False).should_receive("update").never()
        self.libUpdater.currentVersionInfo.version = self.testLibVersion

        self.versionsHandlerHub.setLibVersion(self.testLibVersion)

    def test_setLibVersion_doesDownloadLibsIfHasNotTheRightVersion(self):
        self.libUpdater = flexmock(self.libUpdater).should_receive("update").once()

        self.versionsHandlerHub.setLibVersion(self.testLibVersion)

    def test_setLibVersion_returnsTrue(self):
        self.libUpdater = flexmock(self.libUpdater, update=lambda x: None)
        self.assertTrue(self.versionsHandlerHub.setLibVersion(self.testLibVersion))
        self.assertTrue(self.versionsHandlerHub.setLibVersion(self.testLibVersion))

    def test_setWeb2boardVersion_returnsTrue(self):
        resultObject = Result()
        resultObject.actionDone()
        flexmock(self.updater).should_receive("downloadVersion").and_return(resultObject).once()
        flexmock(self.updater).should_receive("makeAnAuxiliaryCopy").once()
        flexmock(self.updater).should_receive("runAuxiliaryCopy").once()

        self.versionsHandlerHub.setWeb2boardVersion("0.0.1")
