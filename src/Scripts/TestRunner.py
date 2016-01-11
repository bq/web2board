import os
import unittest
from Test import setConfigurationFilesForTest
from Test.HTMLTestRunner import HTMLTestRunner
from Test.integration.testCompilerUploader import TestCompilerUploader
from Test.unit.Updaters.testUpdater import TestUpdater
from Test.unit.WSCommunication.Hubs.testBoardConfigHub import TestBoardConfigHub
from Test.unit.WSCommunication.Hubs.testCodeHub import TestCodeHub
from Test.unit.WSCommunication.Hubs.testSerialMonitorHub import TestSerialMonitorHub
from Test.unit.testUtils import TestUtils
from libs.PathsManager import PathsManager


def __runTests(suite, reportTitle="report"):
    setConfigurationFilesForTest.run()
    reportPath = PathsManager.SETTINGS_PATH + os.sep + reportTitle + '.html'
    runner = HTMLTestRunner(stream=file(reportPath, 'wb'), title=" Web2Board "+reportTitle, verbosity=1)
    # runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)


def runUnitTests():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCodeHub))
    suite.addTests(unittest.makeSuite(TestBoardConfigHub))
    suite.addTests(unittest.makeSuite(TestSerialMonitorHub))
    suite.addTests(unittest.makeSuite(TestUpdater))
    suite.addTests(unittest.makeSuite(TestUtils))
    __runTests(suite, "unitTestReport")


def runIntegrationTests():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCompilerUploader))
    __runTests(suite, "integrationTestReport")


def runAllTests():
    runUnitTests()
    runIntegrationTests()
