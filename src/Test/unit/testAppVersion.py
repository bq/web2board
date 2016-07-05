# coding=utf-8
import os
import unittest

from flexmock import flexmock, flexmock_teardown

from Test.testingUtils import restore_test_resources
from libs.PathsManager import PathsManager
from libs.AppVersion import AppVersion


class TestAppVersion(unittest.TestCase):
    def setUp(self):
        self.test_settings_path = PathsManager.TEST_SETTINGS_PATH + os.sep + "AppVersion"
        restore_test_resources("AppVersion")

    def tearDown(self):
        PathsManager.set_all_constants()
        AppVersion.read_version_values()
        flexmock_teardown()

    def _test_corrupted_file(self, file_name):
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, file_name)
        AppVersion._log = flexmock(AppVersion._log)
        AppVersion._log.should_receive('critical').at_least().times(1)

        AppVersion.read_version_values()

    def test_read_version_values_noVersionFileRaisesIOError(self):
        PathsManager.VERSION_PATH = "noExistingFile"

        self.assertRaises(IOError, AppVersion.read_version_values)

    def test_read_version_values_corruptedFileRaisesValueError(self):
        self._test_corrupted_file("corrupted.version")

    def test_read_version_values_malformedVersionRaisesVersionError(self):
        self._test_corrupted_file("malformedW2BVersion.version")
        self._test_corrupted_file("malformedLibsVersion.version")

    def test_read_version_values_AppVersionSuccessfullyLoaded(self):
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, "correctVersion.version")

        AppVersion.read_version_values()

        self.assertEqual(AppVersion.web2board.version_string, "0.1.1")
        self.assertEqual(AppVersion.libs.version_string, "0.1.2")
        self.assertTrue(AppVersion.libs.compare_libraries_names(["BitbloqButtonPad"]))
        self.assertEqual(AppVersion.libs.url, "http://bitbloq.com")

    def test_store_values_saveAppVersionFile(self):
        AppVersion.web2board.version_string = "0.0.1"
        AppVersion.libs.version_string = "0.1.2"
        AppVersion.libs.libraries_names = ["a"]
        AppVersion.libs.url = "http://aaa.com"
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, "testStoreValues.version")

        AppVersion.store_values()
        AppVersion.web2board.version_string = "1.0.1"
        AppVersion.libs.version_string = "1.1.2"
        AppVersion.libs.libraries_names = ["b"]
        AppVersion.libs.url = "http://bbb.com"
        AppVersion.read_version_values()

        self.assertEqual(AppVersion.web2board.version_string, "0.0.1")
        self.assertEqual(AppVersion.libs.version_string, "0.1.2")
        self.assertTrue(AppVersion.libs.compare_libraries_names(["a"]))
        self.assertEqual(AppVersion.libs.url, "http://aaa.com")

    def test_store_values_nonAsciiCharacters(self):
        AppVersion.libs.url = u"http://aaa.com"
        AppVersion.libs.libraries_names = ["ña", "áéíóú"]
        PathsManager.VERSION_PATH = os.path.join(self.test_settings_path, "testStoreNonAscii.version")

        AppVersion.store_values()
        AppVersion.libs.url = "http://bbb.com"
        AppVersion.libs.libraries_names = ["b"]
        AppVersion.read_version_values()

        self.assertEqual(AppVersion.libs.url, "http://aaa.com")
        self.assertTrue(AppVersion.libs.compare_libraries_names(["ña", "áéíóú"]))

    def test_log_data_logsAppVersionValues(self):
        def log_mock(message):
            messages.append(message)

        AppVersion.web2board.version_string = "0.0.1"
        AppVersion.libs.version_string = "0.1.2"
        AppVersion.libs.libraries_names = ["a"]
        AppVersion.libs.url = "http://aaa.com"
        messages = []
        original_log_info = AppVersion._log.info

        try:
            AppVersion._log.info = log_mock
            AppVersion.log_data()
            self.assertIn("0.0.1", messages[0])
            self.assertIn("0.1.2", messages[1])
            self.assertIn("a", messages[2])
            self.assertIn("http://aaa.com", messages[3])

        finally:
            AppVersion._log.info = original_log_info

    def test_log_data_doesNotRaiseUnicodeError(self):
        AppVersion.libs.libraries_names = ["ña", "áéíóú"]

        try:
            AppVersion.log_data()
        except UnicodeError:
            self.fail("Logging libraries names with non-ascii characters raises UnicodeError")

    # Tests to assert the comparison between web2board versions
    def _compare(self, comparing_values, comparing_function):
        for old_version, new_version in comparing_values:
            AppVersion.web2board.set_version_values(old_version)
            comparing_function(AppVersion.web2board, new_version)

    def test_eq(self):
        equals = [
            ('0.0.0', '0.0.0'),
            ('1.0.0', '1.0.0'),
            ('1.15.0', '1.15.0')
        ]
        self._compare(equals, self.assertEqual)

    def test_ne(self):
        equals = [
            ('0.0.0', '0.0.1'),
            ('1.0.0', '1.2.0'),
            ('1.15.0', '1.5.0')
        ]
        self._compare(equals, self.assertNotEqual)

    def test_gt(self):
        equals = [
            ('1.0.0', '0.1.1'),
            ('1.0.0', '0.99.99'),
            ('1.15.0', '1.14.50')
        ]
        self._compare(equals, self.assertGreater)

    def test_ge(self):
        equals = [
            ('1.0.0', '0.1.1'),
            ('1.0.0', '0.99.99'),
            ('1.15.0', '1.14.50'),
            ('1.15.0', '1.15.0')
        ]
        self._compare(equals, self.assertGreaterEqual)

    def test_lt(self):
        equals = [
            ('0.0.0', '0.1.1'),
            ('3.99.57', '4.00.00'),
            ('1.15.0', '1.16.50'),
            ('1.15.0', '1.15.1')
        ]
        self._compare(equals, self.assertLess)

    def test_le(self):
        equals = [
            ('0.0.0', '0.1.1'),
            ('3.99.57', '4.00.00'),
            ('1.15.0', '1.16.50'),
            ('1.15.0', '1.15.0')
        ]
        self._compare(equals, self.assertLessEqual)

